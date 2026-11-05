# Workflow — Quando o Prazo Dobra

| Beneficiário | Fundamento | Observação |
|---|---|---|
| Fazenda Pública (U/E/M/DF, autarquias, fundações) | CPC art. 183 | Em dobro para **todas** as manifestações; não se aplica quando a lei fixa prazo próprio |
| Ministério Público | CPC art. 180 | Idem |
| Defensoria Pública | CPC art. 186 | Vale também para escritórios de prática jurídica de faculdades e entidades conveniadas (§3º) |
| Litisconsortes com procuradores diferentes, de escritórios distintos | CPC art. 229 | **Só em autos físicos** (§2º exclui processo eletrônico) |
| Réu preso (penal) e Defensoria no processo penal | CPP art. 370 c/ LC 80/94 art. 44, I | Contagem em dobro para a Defensoria |

## Checklist

1. A parte se enquadra em alguma linha da tabela?
2. O processo é eletrônico? (mata a dobra do art. 229)
3. A lei fixa prazo próprio para esse ato? (mata a dobra do art. 183 §2º)
4. Registrar a conclusão com fundamento em `registro-prazos.jsonl` (na pasta do escritório, nunca em repositório público) (`event: "dobra_avaliada"`).

**Regra do escritório:** a dobra da parte **contrária** também importa — ela define quando você pode esperar a manifestação adversa e planejar a réplica.
