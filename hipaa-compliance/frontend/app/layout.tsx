import './globals.css'

export const metadata = {
  title: 'HIPAA Compliance - Security & Compliance',
  description: 'Advanced security & compliance platform',
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
