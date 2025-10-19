# Checklist de Acessibilidade — ConciliaAI Dashboard

> Referência: WCAG 2.1 Nível AA

## 1. Perceptível

- [x] **Contraste de cores:** textos e ícones atendem à razão mínima 4.5:1 (7:1 para elementos críticos).  
- [x] **Texto alternativo:** ícones e CTAs possuem `aria-label` ou `aria-hidden` apropriado.  
- [x] **Layout responsivo:** conteúdo reflow sem scroll horizontal de 320px a 1920px.  
- [x] **Uso de cor:** status acompanhados por texto e ícones (ex.: 🔴 Crítica).

## 2. Operável

- [x] **Acessível via teclado:** todos os botões e links recebem foco e operam com Enter/Espaço.  
- [x] **Indicadores de foco visíveis:** contorno de 2px azul em elementos interativos.  
- [x] **Tempo:** nenhuma interação exige limites temporais; modal pode ser fechado com ESC.  
- [x] **Navegação clara:** ordem de tabulação lógica; link “Pular para o conteúdo” presente.

## 3. Compreensível

- [x] **Linguagem declarada:** `lang="pt-BR"` no HTML.  
- [x] **Linguagem simples:** evita jargões técnicos (NSU, MDR) e prioriza frases curtas.  
- [x] **Consistência:** componentes reutilizam padrões de cor, tipografia e interação.  
- [x] **Assistência:** modal de contestação explica próximos passos e probabilidades.

## 4. Robusto

- [x] **HTML semântico:** uso de `<header>`, `<main>`, `<section>`, `<article>`, `<nav>` e `role` quando necessário.  
- [x] **Compatibilidade ARIA:** modal com `role="dialog"`, atributos `aria-modal`, `aria-labelledby` e `aria-describedby`.  
- [x] **Fallback de movimento:** `prefers-reduced-motion` reduz animações.  
- [x] **Suporte a leitores de tela:** textos informativos evitam abreviações não anunciadas.

## Recomendações Futuras
- Validar contraste em dark mode quando implementado.  
- Adicionar testes automatizados com axe-core no pipeline CI/CD.  
- Incluir legenda ou transcrição para vídeos de onboarding.  
- Revisar textos com especialistas em linguagem simples para garantir leitura em 8º ano escolar.
