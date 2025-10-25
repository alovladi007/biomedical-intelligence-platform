import './globals.css'

export const metadata = {
  title: 'Biosensing Technology - Real-Time Health Monitoring',
  description: 'Advanced real-time health monitoring platform',
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
