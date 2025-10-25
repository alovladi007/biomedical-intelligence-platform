import './globals.css'

export const metadata = {
  title: 'AI Diagnostics - Medical Intelligence Platform',
  description: 'Advanced medical intelligence platform platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
