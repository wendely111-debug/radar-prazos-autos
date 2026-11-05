#!/usr/bin/env python3
"""jus-livre: consultas jurídicas gratuitas em APIs públicas oficiais.

Substitui o Jus MCP (pago) para o uso do dia a dia:
  djen     intimações/publicações do DJEN (CNJ) por OAB ou processo
  datajud  metadados e movimentações de processo (DataJud/CNJ)
  indice   índices do Banco Central (SGS): IPCA, INPC, Selic, IGP-M, TR, IPCA-E
  pncp     licitações publicadas no PNCP

Só biblioteca padrão. Exemplos:
  python jus_livre.py djen --oab 12345 --uf PB --dias 7
  python jus_livre.py datajud 0000001-23.2026.8.15.0001
  python jus_livre.py indice ipca --de 01/01/2025 --ate 30/09/2026 --acumulado
  python jus_livre.py pncp --uf PB --dias 15 --termo "campina grande"
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "radar-prazos-autos/1.0", "Accept": "application/json"}

# Chave pública do DataJud (rotaciona sem aviso; buscamos a atual na wiki e usamos esta como reserva)
DATAJUD_KEY_FALLBACK = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
TR_UF = {"01": "ac", "02": "al", "03": "ap", "04": "am", "05": "ba", "06": "ce", "07": "dft", "08": "es",
         "09": "go", "10": "ma", "11": "mt", "12": "ms", "13": "mg", "14": "pa", "15": "pb", "16": "pr",
         "17": "pe", "18": "pi", "19": "rj", "20": "rn", "21": "rs", "22": "ro", "23": "rr", "24": "sc",
         "25": "se", "26": "sp", "27": "to"}
SERIES = {"ipca": 433, "inpc": 188, "igpm": 189, "ipcae": 10764, "tr": 226, "selic": 11, "selic-meta": 432,
          "selic-mensal": 4390, "cdi": 12}
MENSAIS = {"ipca", "inpc", "igpm", "ipcae", "selic-mensal"}
MODALIDADES = {1: "Leilão eletrônico", 4: "Concorrência eletrônica", 5: "Concorrência presencial",
               6: "Pregão eletrônico", 7: "Pregão presencial", 8: "Dispensa", 9: "Inexigibilidade"}


def http(url, data=None, headers=None, timeout=75, tentativas=4):
    hdr = {**UA, **(headers or {})}
    body = json.dumps(data).encode() if data is not None else None
    if body:
        hdr["Content-Type"] = "application/json"
    for n in range(tentativas):
        try:
            req = urllib.request.Request(url, data=body, headers=hdr, method="POST" if body else "GET")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8", "replace")
                return json.loads(txt) if txt.strip() else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and n < tentativas - 1:
                time.sleep((6 if e.code == 429 else 2) * (n + 1))
                continue
            raise SystemExit(f"Erro HTTP {e.code} em {url.split('?')[0]}")
        except (urllib.error.URLError, TimeoutError) as e:
            if n < tentativas - 1:
                time.sleep(2)
                continue
            raise SystemExit(f"Sem resposta de {url.split('?')[0]}: {e}")


def limpa_html(t, limite=None):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:limite] + "…" if limite and len(t) > limite else t


def datas(args):
    ate = dt.datetime.strptime(args.ate, "%d/%m/%Y").date() if args.ate else dt.date.today()
    de = dt.datetime.strptime(args.de, "%d/%m/%Y").date() if args.de else ate - dt.timedelta(days=args.dias)
    return de, ate


# ---------------- DJEN ----------------
def cmd_djen(a):
    if not a.processo and not (a.oab and a.uf):
        sys.exit("Informe --oab e --uf (ex.: --oab 12345 --uf PB) ou --processo.")
    de, ate = datas(a)
    base = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
    filtros = []
    if a.processo:
        filtros.append({"numeroProcesso": re.sub(r"\D", "", a.processo)})
    else:
        oab = re.sub(r"\D", "", a.oab)
        filtros += [{"numeroOab": oab + suf, "ufOab": a.uf.upper()} for suf in ["", "-O", "-A", "-N", "-B", "-S", "-E"]]
    vistos, itens = set(), []
    for f in filtros:
        pagina = 1
        while True:
            q = {**f, "dataDisponibilizacaoInicio": de.isoformat(), "dataDisponibilizacaoFim": ate.isoformat(),
                 "pagina": pagina, "itensPorPagina": 50}
            d = http(base + "?" + urllib.parse.urlencode(q))
            lote = d.get("items", []) or []
            for i in lote:
                if i.get("id") not in vistos:
                    vistos.add(i.get("id"))
                    itens.append(i)
            if len(lote) < 50 or pagina * 50 >= (d.get("count") or 0) or pagina >= 40:
                break
            pagina += 1
    itens.sort(key=lambda i: i.get("data_disponibilizacao", ""), reverse=True)
    if a.json:
        print(json.dumps(itens, ensure_ascii=False, indent=1))
        return
    grupos = {}
    for i in itens:  # o mesmo ato publicado para vários destinatários vira uma linha só
        chave = (i.get("numero_processo"), i.get("data_disponibilizacao"), i.get("link"), i.get("tipoComunicacao"))
        grupos.setdefault(chave, []).append(i)
    print(f"DJEN {de:%d/%m/%Y} a {ate:%d/%m/%Y} — {len(itens)} comunicação(ões) em {len(grupos)} ato(s)\n")
    for g in grupos.values():
        i = g[0]
        if len(g) > 1:
            print(f"  ({len(g)} comunicações do mesmo ato)")
        print(f"• {i.get('data_disponibilizacao')} | {i.get('siglaTribunal')} | {i.get('numeroprocessocommascara') or i.get('numero_processo')}"
              f" | {i.get('tipoComunicacao')} | {i.get('nomeOrgao')}")
        print(f"  Classe: {i.get('nomeClasse')} | Meio: {i.get('meiocompleto') or i.get('meio')}")
        if a.texto:
            print("  " + limpa_html(i.get("texto"), a.texto))
        if i.get("link"):
            print(f"  Link: {i.get('link')}")
        print()
    print("Aviso: conferir sempre no DJEN oficial (comunica.pje.jus.br) antes de contar prazo.")


# ---------------- DataJud ----------------
def datajud_key():
    try:
        req = urllib.request.Request("https://datajud-wiki.cnj.jus.br/api-publica/acesso/", headers={"User-Agent": "Mozilla/5.0"})
        t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        m = re.search(r"APIKey\s+([A-Za-z0-9+/=_-]{30,})", html.unescape(re.sub(r"<[^>]+>", " ", t)))
        if m:
            return m.group(1)
    except Exception:
        pass
    return DATAJUD_KEY_FALLBACK


def alias(n):
    j, tr = n[13], n[14:16]
    uf, num = TR_UF.get(tr), int(tr)
    if j == "8" and uf:
        return f"api_publica_tj{uf}"
    if j == "4" and 1 <= num <= 6:
        return f"api_publica_trf{num}"
    if j == "5":
        return "api_publica_tst" if tr == "00" else (f"api_publica_trt{num}" if 1 <= num <= 24 else None)
    if j == "6":
        return "api_publica_tse" if tr == "00" else (f"api_publica_tre-{uf}" if uf else None)
    if j == "3" and tr == "00":
        return "api_publica_stj"
    if j == "7" and tr == "00":
        return "api_publica_stm"
    if j == "9" and uf in ("mg", "rs", "sp"):
        return f"api_publica_tjm{uf}"
    return None


def fmt_data(v):
    v = str(v or "")
    if re.fullmatch(r"\d{14}", v):
        return f"{v[6:8]}/{v[4:6]}/{v[:4]} {v[8:10]}:{v[10:12]}"
    if re.fullmatch(r"\d{13}", v):
        return dt.datetime.fromtimestamp(int(v) / 1000).strftime("%d/%m/%Y %H:%M")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T?(\d{2})?:?(\d{2})?", v)
    return f"{m[3]}/{m[2]}/{m[1]}" + (f" {m[4]}:{m[5]}" if m and m[4] else "") if m else v


def cmd_datajud(a):
    n = re.sub(r"\D", "", a.processo)
    if len(n) != 20:
        raise SystemExit("Número CNJ inválido (precisa de 20 dígitos).")
    al = alias(n)
    if not al:
        raise SystemExit("Esse segmento (STF/CNJ) não integra o DataJud.")
    d = http(f"https://api-publica.datajud.cnj.jus.br/{al}/_search", {"query": {"match": {"numeroProcesso": n}}},
             {"Authorization": "APIKey " + datajud_key()})
    hits = d.get("hits", {}).get("hits", [])
    if not hits:
        parcial = (d.get("_shards") or {}).get("failed", 0)
        raise SystemExit("Resposta parcial do DataJud (cluster saturado) — tente de novo." if parcial
                         else "Não encontrado no DataJud (indexação pode atrasar semanas). Conferir no PJe.")
    for h in hits:
        s = h["_source"]
        if a.json:
            print(json.dumps(s, ensure_ascii=False, indent=1))
            continue
        print(f"Processo {s.get('numeroProcesso')} — {s.get('tribunal')} ({al}) — grau {s.get('grau')}")
        print(f"Classe: {(s.get('classe') or {}).get('nome')} | Órgão: {(s.get('orgaoJulgador') or {}).get('nome')}")
        print(f"Ajuizamento: {fmt_data(s.get('dataAjuizamento'))} | Sigilo: {s.get('nivelSigilo')} | Atualizado: {fmt_data(s.get('dataHoraUltimaAtualizacao'))}")
        print("Assuntos: " + "; ".join(x.get("nome", "") for x in (s.get("assuntos") or []) if isinstance(x, dict)))
        movs = sorted(s.get("movimentos") or [], key=lambda m: str(m.get("dataHora")), reverse=True)
        print(f"\nÚltimas {min(a.movs, len(movs))} de {len(movs)} movimentações:")
        for m in movs[: a.movs]:
            comp = "; ".join(f"{c.get('nome')}: {c.get('descricao') or c.get('valor')}" for c in (m.get("complementosTabelados") or []))
            print(f"  {fmt_data(m.get('dataHora'))} — {m.get('nome')}" + (f" ({comp})" if comp else ""))
        print()
    print("Aviso: o DataJud não traz o teor de decisões nem intimações (use `djen`).")


# ---------------- Índices BCB ----------------
def cmd_indice(a):
    nome = a.serie.lower()
    cod = SERIES.get(nome) or (int(nome) if nome.isdigit() else None)
    if not cod:
        raise SystemExit("Série desconhecida. Use: " + ", ".join(SERIES))
    de, ate = datas(a)
    url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{cod}/dados?formato=json"
           f"&dataInicial={de:%d/%m/%Y}&dataFinal={ate:%d/%m/%Y}")
    rows = http(url)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False))
        return
    for r in rows if (nome in MENSAIS or len(rows) <= 40) else rows[-10:]:
        print(f"{r['data']}  {r['valor']}%")
    if a.acumulado:
        f = 1.0
        for r in rows:
            f *= 1 + float(r["valor"]) / 100
        print(f"\nAcumulado {nome.upper()} ({rows[0]['data']} a {rows[-1]['data']}, {len(rows)} períodos): "
              f"{(f - 1) * 100:.4f}% — fator {f:.6f}")
        if a.valor:
            print(f"R$ {a.valor:,.2f} atualizado = R$ {a.valor * f:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"\nFonte: BCB/SGS série {cod}. Acumulado = produto dos fatores (não soma).")


# ---------------- PNCP ----------------
def cmd_pncp(a):
    de, ate = datas(a)
    mods = [a.modalidade] if a.modalidade else [6, 8, 4, 9]
    achados = []
    for m in mods:
        for pagina in range(1, a.paginas + 1):
            q = {"dataInicial": f"{de:%Y%m%d}", "dataFinal": f"{ate:%Y%m%d}", "codigoModalidadeContratacao": m,
                 "pagina": pagina, "tamanhoPagina": 50}
            if a.uf:
                q["uf"] = a.uf.upper()
            time.sleep(1.2)  # o PNCP bloqueia rajadas (429)
            d = http("https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?" + urllib.parse.urlencode(q))
            for c in d.get("data") or []:
                txt = " ".join(str(c.get(k, "")) for k in ("objetoCompra",)) + " " + str((c.get("unidadeOrgao") or {}).get("municipioNome", "")) \
                      + " " + str((c.get("orgaoEntidade") or {}).get("razaoSocial", ""))
                if not a.termo or a.termo.lower() in txt.lower():
                    achados.append(c)
            if (d.get("paginasRestantes") or 0) == 0:
                break
    print(f"PNCP {de:%d/%m/%Y}–{ate:%d/%m/%Y} — {len(achados)} contratação(ões)\n")
    for c in achados[: a.limite]:
        u, o = c.get("unidadeOrgao") or {}, c.get("orgaoEntidade") or {}
        print(f"• {MODALIDADES.get(c.get('modalidadeId'), c.get('modalidadeNome'))} | {o.get('razaoSocial')} — {u.get('municipioNome')}/{u.get('ufSigla')}")
        print(f"  {limpa_html(c.get('objetoCompra'), 220)}")
        v = c.get("valorTotalEstimado")
        print(f"  Estimado: {('R$ %.2f' % v) if v else '—'} | Situação: {c.get('situacaoCompraNome')} | Controle: {c.get('numeroControlePNCP')}\n")


def main():
    p = argparse.ArgumentParser(description="Consultas jurídicas gratuitas (DJEN, DataJud, BCB, PNCP)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def periodo(sp, dias):
        sp.add_argument("--de", help="dd/mm/aaaa")
        sp.add_argument("--ate", help="dd/mm/aaaa (padrão: hoje)")
        sp.add_argument("--dias", type=int, default=dias, help=f"janela se --de omitido (padrão {dias})")
        sp.add_argument("--json", action="store_true")

    s = sub.add_parser("djen", help="intimações/publicações")
    s.add_argument("--oab", help="número da OAB (só dígitos); obrigatório se não usar --processo")
    s.add_argument("--uf", help="UF da OAB, ex.: PB")
    s.add_argument("--processo")
    s.add_argument("--texto", type=int, nargs="?", const=600, default=0, help="mostrar texto (n caracteres)")
    periodo(s, 7)
    s.set_defaults(f=cmd_djen)

    s = sub.add_parser("datajud", help="processo por número CNJ")
    s.add_argument("processo")
    s.add_argument("--movs", type=int, default=15)
    s.add_argument("--json", action="store_true")
    s.set_defaults(f=cmd_datajud)

    s = sub.add_parser("indice", help="índices BCB")
    s.add_argument("serie", help=", ".join(SERIES) + " ou código SGS")
    s.add_argument("--acumulado", action="store_true")
    s.add_argument("--valor", type=float, help="valor a atualizar pelo acumulado")
    periodo(s, 365)
    s.set_defaults(f=cmd_indice)

    s = sub.add_parser("pncp", help="licitações PNCP")
    s.add_argument("--uf")
    s.add_argument("--termo", help="filtra objeto/órgão/município")
    s.add_argument("--modalidade", type=int, help="6 pregão, 8 dispensa, 4 concorrência, 9 inexigibilidade")
    s.add_argument("--paginas", type=int, default=3)
    s.add_argument("--limite", type=int, default=30)
    periodo(s, 15)
    s.set_defaults(f=cmd_pncp)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
