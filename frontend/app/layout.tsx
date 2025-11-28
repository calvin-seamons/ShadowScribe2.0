import type { Metadata } from 'next'
import './globals.css'
import AppInitializer from '@/components/AppInitializer'

export const metadata: Metadata = {
  title: 'ShadowScribe 2.0',
  description: 'D&D Character Management & AI Assistant',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="font-sans antialiased">
        <AppInitializer>
          {children}
        </AppInitializer>
      </body>
    </html>
  )
}
