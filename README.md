# matriz_avaliativa
Dashboard

## Metodologia e Interpretação dos Gráficos

### Metodologia do Dashboard
O dashboard foi desenvolvido para analisar e comparar o desempenho dos Ceasas em diferentes blocos temáticos de avaliação. Os dados são extraídos de uma planilha Excel estruturada com MultiIndex, onde cada linha representa uma atividade avaliada dentro de um bloco, para cada Ceasa/região.

- **Extração dos Dados:**
  - O sistema lê a planilha e organiza os dados por Bloco, Atividade e Ceasa.
  - Calcula automaticamente as pontuações por bloco, por atividade e os percentuais de desempenho em relação ao total do bloco e à matriz.

- **Filtros Interativos:**
  - É possível filtrar por Ceasa, Bloco, Atividade e faixa de pontuação, além de escolher o tipo de visualização (Gráfico de Barras, Radar ou Tabela).
  - Os filtros permitem análises comparativas detalhadas e personalizadas.

### Gráficos Representados

#### 1. **Pontuação por Bloco do Ceasa**
- Mostra a pontuação absoluta de cada Ceasa em cada bloco temático.
- As cores destacam a região GLOBAL em azul e os demais Ceasas em tons de verde.
- Permite comparar rapidamente o desempenho entre Ceasas em cada bloco.

#### 2. **Distribuição Percentual dos Ceasas**
- Exibe a distribuição percentual do desempenho de cada Ceasa, de acordo com o tipo de percentual selecionado:
  - **% em relação ao Bloco:** Percentual da pontuação do Ceasa em relação ao total do bloco selecionado.
  - **% em relação ao Total do Bloco:** Percentual médio das atividades daquele Ceasa em relação ao total do bloco (média das atividades).
  - **% em relação à Matriz Total:** Percentual médio das atividades daquele Ceasa em relação ao total da matriz.
- O filtro de bloco é habilitado apenas para o tipo "% em relação ao Bloco".
- As cores seguem o mesmo padrão do gráfico anterior.

#### 3. **Radar (Perfil dos Blocos por Ceasa)**
- Mostra o perfil de desempenho de cada Ceasa em todos os blocos simultaneamente.
- Cada linha representa um Ceasa, permitindo visualizar pontos fortes e fracos em cada bloco.
- As cores são consistentes com os outros gráficos.

#### 4. **Tabela**
- Exibe todos os dados detalhados, incluindo atividades, pontuações e percentuais.
- Permite filtros avançados por Ceasa, Bloco, Atividade e faixa de pontuação.
- Os percentuais são apresentados já formatados para facilitar a leitura.

### Interpretação dos Percentuais
- **% em relação ao Bloco:** Mede o quanto o Ceasa atingiu do total possível daquele bloco.
- **% em relação ao Total do Bloco:** Média dos percentuais das atividades daquele bloco para o Ceasa.
- **% em relação à Matriz Total:** Média dos percentuais das atividades em relação ao total geral da matriz.

Essas métricas permitem identificar rapidamente quais Ceasas se destacam em cada bloco, onde estão as maiores oportunidades de melhoria e realizar comparações justas entre diferentes realidades.
