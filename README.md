# Radar de Prazos e Autos

Presente da palestra **"Do Prompt à Petição"**, de WS Advogados Associados.

Uma skill para o Claude que junta duas tarefas do escritório:

1. **Prazos no DJEN**: varre as intimações do Diário de Justiça Eletrônico Nacional (CNJ) pela sua OAB e conta o prazo fatal, com feriados, recesso e a suspensão do art. 220 do CPC.
2. **Leitura de autos**: lê autos, sentenças e acórdãos longos em PDF e devolve linha do tempo, mapa de provas, quadro de teses e estado do processo, citando a folha ou o ID.

## Baixar

| Arquivo | Para quê |
|---|---|
| [**Presente-Radar-Prazos-Autos.rar**](https://github.com/wendely111-debug/radar-prazos-autos/releases/latest/download/Presente-Radar-Prazos-Autos.rar) | Pacote completo (WinRAR), com o guia de instalação |
| [**radar-prazos-autos.zip**](https://github.com/wendely111-debug/radar-prazos-autos/releases/latest/download/radar-prazos-autos.zip) | Só a skill, pronta para enviar no claude.ai (abre também no celular) |

## Instalar

**claude.ai (navegador ou aplicativo):** Configurações > Capacidades > Skills > envie o `radar-prazos-autos.zip` e ative. Peça: *"Tem intimação nova para a OAB 12345/PB?"*

**Claude Code:** copie a pasta `radar-prazos-autos` para `~/.claude/skills/` (no Windows, `C:\Users\SEU-USUARIO\.claude\skills\`). Precisa do Python 3.

Teste sem IA, dentro da pasta da skill:

```
python scripts/prazo_calc.py --disponibilizacao 2026-11-06 --dias 15 --tribunal nacional
python scripts/jus_livre.py djen --oab 12345 --uf PB --dias 7
```

## Limites

- A IA calcula e organiza; quem decide, confere e assina é o advogado. **Confira todo prazo no sistema do tribunal.**
- O DJEN só responde a conexões do Brasil. "Nada encontrado" não prova que não há intimação.
- Os calendários trazem 2026 completo (nacional, TJPB e TRF5) e só os feriados nacionais de 2027. Acrescente os do seu tribunal e da sua comarca em `scripts/feriados*.txt`.
- Não coloque autos de clientes em ferramenta sem contrato e sem treinamento desativado.
- Material educativo, sem garantia. Não é consultoria jurídica.

## Créditos

Feito a partir de skills abertas sob licença MIT: [`djen`](radar-prazos-autos/licencas/LICENSE-djen-Ricardo-Sanches.txt), de Ricardo Sanches; [`prazo-sentinel`](radar-prazos-autos/licencas/LICENSE-prazo-sentinel-Nei-Maciel.txt) e [`resumo-autos`](radar-prazos-autos/licencas/LICENSE-resumo-autos-Nei-Maciel.txt), de Nei Maciel.

Wendley Steffan Ferreira dos Santos · OAB/PB 27.884 · Instagram @WendleySteffan
