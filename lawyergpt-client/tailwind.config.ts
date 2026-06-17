import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sidebar: '#202123',
        'sidebar-hover': '#2a2b32',
        chat: '#343541',
        'chat-input': '#40414f',
        'user-bubble': '#19c37d',
        'assistant-text': '#ececf1',
      },
    },
  },
  plugins: [],
}

export default config
