import './globals.css'

export const metadata = {
  title: 'Drug Discovery AI - Accelerated Pharmaceutical Research',
  description: 'Accelerated pharmaceutical research with molecular modeling and clinical trial optimization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
