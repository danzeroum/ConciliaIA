# Princípios de UX Aplicados

## 1. Don't Make Me Think (Steve Krug)
- **Autoexplicativo:** termos como “Recuperar agora” e “Venda não recebida” substituem jargões técnicos.  
- **Escaneabilidade:** números críticos em fontes 32–36px, descrições curtas e alinhamento consistente.  
- **Menos cliques:** fluxo de contestação reduzido para um único botão com feedback imediato.  
- **Sinais claros:** botões parecem botões, com cores e sombras que indicam interação.

## 2. Hierarquia Visual & Lei de Fitts
- **Prioridade 1:** divergências críticas em destaque (borda vermelha, CTA verde grande).  
- **Prioridade 2:** divergências médias/altas agrupadas em cards secundários.  
- **Prioridade 3:** detalhes técnicos ocultos até solicitação do usuário.  
- **Alvos grandes:** CTAs primários com altura mínima de 48px em mobile e 56px em desktop.

## 3. Progressive Disclosure
- **Nível 1 — Dashboard:** três métricas principais + ação primária.  
- **Nível 2 — Lista de divergências:** cards visuais com resumo humano e CTA direto.  
- **Nível 3 — Detalhes:** timeline, possíveis causas, opções adicionais (contestar, ignorar, resolver).  
- **Detalhes técnicos:** acessados apenas via expansão, evitando sobrecarga inicial.

## 4. Material Design Adaptado
- **Elevação:** sombras `--shadow-md` e `--shadow-lg` sinalizam interatividade.  
- **Motion:** transições de 250ms com fallback para `prefers-reduced-motion`.  
- **Cores:** tokens alinhados à paleta Material (Blue, Red, Orange, Yellow, Green).  
- **Tipografia:** Inter como alternativa moderna ao Roboto, mantendo coerência visual.

## 5. Acessibilidade como Padrão
- **Contraste:** cores validadas para WCAG AA.  
- **Teclado:** navegação completa com foco visível e escape no modal.  
- **Semântica:** uso de elementos HTML adequados (section, article, nav).  
- **Idioma:** `lang="pt-BR"` garante leitura correta por leitores de tela.
