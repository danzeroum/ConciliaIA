module.exports = {
  testEnvironment: 'node',
  testMatch: [
    '<rootDir>/tests/unit/services/**/*.test.ts',
    '<rootDir>/tests/unit/utils/**/*.test.ts',
    '<rootDir>/tests/integration/*.test.ts',
  ],
  collectCoverageFrom: [
    'src/app.ts',
    'src/modules/**/*.ts',
    'src/utils/**/*.ts',
    '!src/middleware/**/*.ts',
    '!src/modules/products/services/**/*.ts',
  ],
  coverageDirectory: 'coverage',
  transform: {
    '^.+\\.(t|j)sx?$': [
      'ts-jest',
      {
        tsconfig: '<rootDir>/tsconfig.jest.json',
      },
    ],
  },
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  moduleNameMapper: {
    '^src/(.*)$': '<rootDir>/src/$1',
  },
};
