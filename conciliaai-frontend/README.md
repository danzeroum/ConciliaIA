# ConciliaAI Frontend

Sistema de Reconciliação Financeira - Interface Web

## 🚀 Quick Start

### Pré-requisitos

- Node.js 20 LTS
- pnpm 8+

### Instalação

```bash
# Instalar dependências
pnpm install

# Copiar arquivo de ambiente
cp .env.example .env.development

# Iniciar servidor de desenvolvimento
pnpm dev
```

A aplicação estará disponível em: http://localhost:3000

## 📦 Scripts Disponíveis

```bash
# Desenvolvimento
pnpm dev              # Inicia servidor de desenvolvimento
pnpm build            # Build para produção
pnpm preview          # Preview do build de produção

# Qualidade de Código
pnpm lint             # Executar ESLint
pnpm lint:fix         # Corrigir erros do ESLint
pnpm format           # Formatar código com Prettier
pnpm type-check       # Verificar tipos TypeScript

# Testes
pnpm test:unit        # Testes unitários
pnpm test:unit:watch  # Testes unitários em watch mode
pnpm test:unit:coverage # Testes com cobertura
pnpm test:e2e         # Testes E2E
pnpm test:all         # Todos os testes

# Documentação
pnpm storybook        # Iniciar Storybook
```

## 🏗️ Estrutura do Projeto

```
src/
├── api/              # Clientes de API
├── components/       # Componentes React
│   ├── common/       # Componentes reutilizáveis
│   ├── layout/       # Componentes de layout
│   └── features/     # Componentes de features
├── hooks/            # Custom hooks
├── pages/            # Páginas
├── store/            # State management (Zustand)
├── theme/            # Tema Material-UI
├── types/            # TypeScript types
└── utils/            # Utilitários
```

## 🛠️ Tecnologias

- **React 18** - Framework UI
- **TypeScript** - Tipagem estática
- **Material-UI** - Componentes UI
- **React Router** - Roteamento
- **Zustand** - State management
- **React Query** - Data fetching
- **React Hook Form** - Formulários
- **Vite** - Build tool

## 📖 Documentação

- [Especificação Frontend](docs/FRONTEND-SPECIFICATION.md)
- [Guia de Desenvolvimento](docs/DEVELOPMENT.md)
- [API Documentation](http://localhost:8000/docs)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 License

Proprietary - ConciliaAI © 2025
