# Workflow — Prazo Perdido (emergência)

> Fundamento: CPC art. 223 §1º (justa causa) · CED-OAB (dever de informar) · apólice de RC profissional.

**Pare. Respire. Siga o runbook — improvisar agora piora.**

## Hora 0 — Confirmar e conter

1. **Recontar o prazo** com `workflows/contagem-prazo.md` — 1 em cada 3 "prazos perdidos" é erro de contagem (feriado local, dobra, suspensão que salvam o prazo)
2. Confirmado o vencimento: **registrar o momento da descoberta** (`event: "prazo_perdido_detectado"`)
3. Comunicar o **sócio responsável** imediatamente — nunca esconder

## Hora 0–24 — Avaliar as saídas técnicas

| Saída | Quando cabe |
|---|---|
| **Justa causa** (CPC art. 223 §1º) | Evento alheio à vontade impediu a prática (sistema do tribunal fora do ar — juntar print/protocolo de indisponibilidade; doença súbita comprovada) |
| **Indisponibilidade do sistema** | Res. CNJ 185/2013 e normas do tribunal: indisponibilidade prorroga o prazo para o 1º dia útil seguinte — buscar o relatório oficial de indisponibilidade |
| **Ato ainda praticável por outra via** | Ex.: perdeu apelação → avaliar ação rescisória (prazo de 2 anos, CPC art. 966) ou querela nullitatis, conforme o vício |
| **Preclusão consumada sem saída** | Reconhecer, mitigar dano e ir ao passo seguinte |

## Hora 24–72 — Cliente e seguro

1. **Informar o cliente por escrito** — CED-OAB exige; ocultar transforma erro em infração ética
2. **Notificar a seguradora de RC profissional** — apólices exigem aviso imediato do fato potencialmente indenizável
3. Documentar tudo em `registro-prazos.jsonl` (na pasta do escritório, nunca em repositório público)

## Pós-mortem (até 7 dias)

- Causa raiz: contagem errada? intimação não vista? responsável ausente sem substituto?
- Corrigir o processo (agenda semanal, dupla checagem, substituto obrigatório)
- Registrar `event: "postmortem_prazo"` com a mudança implementada
