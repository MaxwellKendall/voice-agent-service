/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string
  readonly VITE_SUPABASE_PUBLISHABLE_API_KEY: string
  readonly VITE_OPENAI_API_KEY: string
  readonly VITE_RECIPE_API_URL: string
  readonly VITE_WEBSOCKET_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
