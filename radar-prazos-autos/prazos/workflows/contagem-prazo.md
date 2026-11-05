# Workflow — Contagem de Prazo

> Fundamento: CPC art. 219, 224, 231 · CLT art. 775 · CPP art. 798 · Lei 11.419/2006 art. 5º.

## Passo 1 — Coletar os 5 dados obrigatórios

1. **Ato processual** (contestação, apelação, embargos, RO...) → prazo-base em `lib/regras-contagem.md`
2. **Data e meio da intimação** (DJe? portal? mandado? carta?)
3. **Justiça/rito** → define o regime (úteis × corridos)
4. **Parte tem prerrogativa de dobra?** → `workflows/dobra-prazo.md`
5. **Tribunal** → calendário de feriados aplicável

Faltou dado → **pergunte**. Nunca assuma o meio de intimação.

## Passo 2 — Determinar o dia do início

| Meio | Regra do termo inicial |
|---|---|
| DJe (publicação) | Dia útil seguinte à publicação = data da intimação; conta-se do dia útil seguinte (CPC art. 224 §§2º-3º) |
| Portal eletrônico (PJe/eproc) | Consulta em até 10 dias corridos; sem consulta, intimação ficta no 10º dia (Lei 11.419 art. 5º §3º) |
| Mandado (oficial) | Data da juntada do mandado aos autos (CPC art. 231, II) |
| Carta (AR) | Data da juntada do AR (CPC art. 231, I) |
| Audiência | Intimação em audiência conta dali (art. 1.003 §1º para sentença em audiência) |

## Passo 3 — Contar no regime certo

- **CPC**: só dias úteis (art. 219). Exclui o dia do começo, inclui o do vencimento (art. 224).
- **CLT**: dias úteis desde a Lei 13.467/2017 (art. 775). Recurso ordinário: 8 dias.
- **CPP**: dias **corridos** (art. 798 §1º); vencimento em dia sem expediente prorroga para o próximo útil.
- **JEC**: CPC subsidiário — dias úteis.
- Suspensão 20/12–20/01 (CPC art. 220) **suspende** — retoma do saldo, não recomeça.

## Passo 4 — Emitir no formato padrão + evidência

```json
{"ts":"<ISO>","event":"prazo_ciencia","case_id":"<>","payload":{"ato":"apelacao","intimacao":"2026-07-01","fatal":"2026-07-22","regime":"cpc-uteis","dobra":false},"actor":"<quem calculou>"}
```

## Armadilhas frequentes

- Feriado **local** (padroeiro da comarca) que não está no calendário nacional → sempre checar `lib/feriados-2026.md` do tribunal
- Embargos de declaração: **5 dias** e interrompem (não suspendem) o prazo dos demais recursos (CPC art. 1.026)
- Prazo em dobro **não se aplica** a litisconsortes em autos eletrônicos (CPC art. 229 §2º)
- Prescrição/decadência correm no recesso — são prazos materiais
