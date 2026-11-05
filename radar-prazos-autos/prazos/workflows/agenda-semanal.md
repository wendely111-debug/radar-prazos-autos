# Workflow — Agenda Semanal de Prazos (rotina de segunda-feira)

> Objetivo: nenhum prazo da semana descobre o advogado de surpresa.

## Rotina (30 min, toda segunda 8h30)

1. **Varrer** a planilha `templates/controle-prazos.md` (ou o sistema do escritório) → todos os prazos com fatal nos próximos **10 dias úteis**
2. **Classificar** por criticidade:
   - 🔴 Fatal esta semana e peça não iniciada
   - 🟡 Fatal esta semana com peça em andamento
   - 🟢 Fatal na próxima semana
3. **Conferir responsável** — cada prazo 🔴/🟡 tem dono nomeado e substituto (férias/audiência)
4. **Recontar os 🔴** — erro de contagem se descobre recontando, não confiando
5. **Emitir o quadro da semana** e registrar (`event: "agenda_semanal"`)

## Quadro padrão

```
SEMANA {{01-05/07}} — {{n}} prazos
🔴 {{22/07}} Apelação · Caso {{X}} · resp. {{Dr. A}} · peça NÃO iniciada → ação hoje
🟡 {{24/07}} Contestação · Caso {{Y}} · resp. {{Dra. B}} · minuta em revisão
🟢 {{29/07}} Réplica · Caso {{Z}} · resp. {{Dr. A}}
```

## KPIs

| Métrica | Meta |
|---|---|
| Prazos protocolados até D-2 | ≥ 80% |
| Protocolo em D-0 (dia fatal) | < 5% |
| Prazo perdido | **0** |
