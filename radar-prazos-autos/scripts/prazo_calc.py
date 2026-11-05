#!/usr/bin/env python3
"""prazo-calc — contagem de prazos processuais.

Uso:
  python3 prazo_calc.py --intimacao 2026-07-01 --dias 15 --regime uteis
  python3 prazo_calc.py --disponibilizacao 2026-10-09 --dias 15            # data do DJEN
  python3 prazo_calc.py --intimacao 2026-07-01 --dias 8 --regime uteis --dobra
  python3 prazo_calc.py --intimacao 2026-07-01 --dias 5 --regime corridos --tribunal trf5

Regimes: uteis (CPC/CLT) | corridos (CPP art. 798; Súm. 310 STF)
Calendários: --tribunal tjpb (padrão) | trf5 | nacional  → feriados-<tribunal>.txt / feriados.txt
Aplica: exclusão do dia do começo (CPC art. 224), feriados e pontos facultativos do tribunal,
recesso forense 20/12–06/01 (sem expediente, ambos os regimes) e suspensão do CPC art. 220
(20/12–20/01, só regime 'uteis'). Com --disponibilizacao aplica a Lei 11.419/2006 art. 4º §§3º-4º.
"""
import argparse, datetime as dt, pathlib, sys

sys.stdout.reconfigure(encoding="utf-8")

def load_holidays(tribunal="tjpb"):
    nome = "feriados.txt" if tribunal == "nacional" else f"feriados-{tribunal}.txt"
    f = pathlib.Path(__file__).parent / nome
    if not f.exists():
        return set()
    out = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip().split("#")[0].strip()
        if line:
            out.add(dt.date.fromisoformat(line))
    return out

def in_recess(d: dt.date) -> bool:
    # suspensão de prazos do CPC art. 220
    return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20)

def in_forensic_recess(d: dt.date) -> bool:
    # recesso forense 20/12 a 06/01: sem expediente, vale também para prazos corridos
    return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 6)

def is_court_day(d: dt.date, holidays, use_recess) -> bool:
    if d.weekday() >= 5 or d in holidays or in_forensic_recess(d):
        return False
    if use_recess and in_recess(d):
        return False
    return True

def next_court_day(d, holidays, use_recess):
    while not is_court_day(d, holidays, use_recess):
        d += dt.timedelta(days=1)
    return d

def publicacao_djen(disponibilizacao: dt.date, holidays):
    # Lei 11.419/2006 art. 4º §3º: publicação = 1º dia útil seguinte à disponibilização
    return next_court_day(disponibilizacao + dt.timedelta(days=1), holidays, False)

def count(intimacao: dt.date, dias: int, regime: str, holidays):
    uteis = regime == "uteis"
    # exclui o dia do começo (art. 224): contagem inicia no dia seguinte
    d = intimacao + dt.timedelta(days=1)
    if uteis:
        d = next_court_day(d, holidays, True)
        restante = dias
        while restante > 1:
            d = next_court_day(d + dt.timedelta(days=1), holidays, True)
            restante -= 1
        return d
    # corridos: começa no 1º dia com expediente (Súm. 310 STF), corre sem interrupção
    # e prorroga se o último dia cair em dia sem expediente (CPP art. 798 §3º)
    inicio = next_court_day(d, holidays, False)
    fatal = inicio + dt.timedelta(days=dias - 1)
    return next_court_day(fatal, holidays, False)

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--intimacao", help="data da intimação/publicação AAAA-MM-DD")
    g.add_argument("--disponibilizacao", help="data de disponibilização no DJEN AAAA-MM-DD")
    p.add_argument("--dias", type=int, required=True)
    p.add_argument("--regime", choices=["uteis", "corridos"], default="uteis")
    p.add_argument("--dobra", action="store_true", help="prazo em dobro (art. 183/186/229)")
    p.add_argument("--tribunal", choices=["tjpb", "trf5", "nacional"], default="tjpb",
                   help="calendário de feriados (padrão: tjpb)")
    a = p.parse_args()

    holidays = load_holidays(a.tribunal)
    dias = a.dias * 2 if a.dobra else a.dias
    if a.disponibilizacao:
        disp = dt.date.fromisoformat(a.disponibilizacao)
        intim = publicacao_djen(disp, holidays)
        print(f"[prazo-sentinel] DJEN: disponibilizado em {disp} → publicação em {intim}")
    else:
        intim = dt.date.fromisoformat(a.intimacao)
    fatal = count(intim, dias, a.regime, holidays)

    print(f"[prazo-sentinel] {a.tribunal.upper()} · intimação {intim} · {dias} dias {a.regime}"
          + (" (EM DOBRO)" if a.dobra else ""))
    print(f"PRAZO FATAL: {fatal} ({fatal.strftime('%A')})")
    for delta, label in [(5, "D-5"), (3, "D-3"), (1, "D-1")]:
        d = fatal
        n = delta
        while n > 0:
            d -= dt.timedelta(days=1)
            if is_court_day(d, holidays, a.regime == "uteis"):
                n -= 1
        print(f"alerta {label}: {d}")
    if not holidays:
        print("⚠️  arquivo de feriados vazio/ausente — só fins de semana considerados. "
              "Preencha com os feriados do tribunal!")
    elif max(holidays).year < fatal.year:
        print(f"⚠️  calendário {fatal.year} do {a.tribunal.upper()} ainda não cadastrado: "
              "confira os feriados no site do tribunal e atualize o arquivo.")

if __name__ == "__main__":
    main()
