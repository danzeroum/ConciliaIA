# Design System — ConciliaAI

## Princípios
1. **Não me faça pensar:** linguagem natural, hierarquia visual agressiva e CTAs evidentes.  
2. **Mobile-first:** componentes pensados para 320px com expansão progressiva para desktop.  
3. **Progressive disclosure:** informações técnicas disponíveis somente quando necessárias.  
4. **Acessibilidade primeiro:** contraste mínimo 4.5:1, estados de foco visíveis e sem dependência de cor.

## Design Tokens
Os tokens base estão definidos em [`design/prototype/design-tokens.css`](../../design/prototype/design-tokens.css).

### Paleta de Cores
- **Criticidade:** vermelho 700, laranja 700, amarelo 700, roxo 700.  
- **Sucesso:** verde 700.  
- **Marca:** azul 700, com variantes light/dark.  
- **Fundos:** cinza 50 para plano de fundo global, branco para superfícies.

### Tipografia
- **Fonte:** Inter (fallbacks nativos).  
- **Escala:** 12, 14, 16, 18, 24, 32px.  
- **Pesos:** 400, 500, 600, 700.  
- **Regras:** textos críticos em 32–36px, meta-informações em 12–14px.

### Espaçamento e Layout
- Grid baseado em múltiplos de 4px (4 até 48px).  
- Containers com largura máxima de 1200px.  
- Cards com raio de 12px e sombras Material (z2/z4).  
- Animações suaves de 250ms.

## Componentes

### MetricCard
- **Variantes:** primário (gradiente azul) e secundário (branco).  
- **Conteúdo:** ícone à esquerda, label em caixa alta, valor principal e meta-info.  
- **Uso:** destaque para valores chave (perdido, recuperável, recuperado).

### DivergenceCard
- **Propriedades:** severidade, título, amount, descrição, daysOld, acquirer, ação primária.  
- **Visuais:** borda esquerda 4px na cor da severidade; gradiente suave de fundo.  
- **Ação:** botão “Recuperar agora” + link secundário “Ver detalhes”.

### SeverityBadge
- **Variantes:** crítica, alta, média, baixa.  
- **Formato:** pílula com ícone emoji, texto uppercase e borda contrastante.  
- **Uso:** destacam filtros, títulos de seção e cards.

### RecoverButton
- **Estado padrão:** verde 600, ícone 💰 alinhado à esquerda.  
- **Estados:** hover (verde 700 + sombra), active (verde 800), disabled (cinza 300), loading (“Processando…” + spinner).  
- **Acessibilidade:** `aria-label` com valor dinâmico a ser recuperado.

### Timeline
- **Estrutura:** lista de etapas numeradas (emoji 1️⃣, 2️⃣, 3️⃣).  
- **Uso:** explicar próximos passos pós-contestação.  
- **Feedback:** textos curtos com verbos no presente.

### Modal
- **Semântica:** `role="dialog"`, overlay com blur e fechamento por ESC/clique externo.  
- **Layout:** conteúdo centralizado com radius 16px e sombra forte.  
- **Ações:** primária “Ver próxima divergência”, secundária “Voltar ao dashboard”.

## Padrões de Interação
- **Contestação 1-click:** sempre enfatizar CTA verde com feedback imediato.  
- **Agrupamento por severidade:** listas críticas exibidas expandido; média/baixa colapsadas.  
- **Comparativos multi-loja:** ranking ordenado, destaque para lojas em atenção com ícone de alerta.  
- **Atualizações em tempo real:** valores críticos com `aria-live` para avisar sobre mudanças.

## Responsividade
- **Mobile (≤ 768px):** cards empilhados, botões largura total, navegação em coluna.  
- **Tablet (769–1023px):** duas colunas para métricas secundárias, cards com espaçamento médio.  
- **Desktop (≥ 1024px):** grid completo, timeline e modais centralizados.

## Governança
- Versão inicial `v0.1`.  
- Atualizações documentadas via changelog no time de DesignOps.  
- Componentes implementados em React devem importar tokens via CSS variables para garantir consistência.
