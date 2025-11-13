import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import AppInitializer from '@/components/AppInitializer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ShadowScribe 2.0',
  description: 'D&D Character Management & AI Assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppInitializer>
          {children}
        </AppInitializer>
      </body>
    </html>
  )
}
