import './globals.css';

export const metadata = {
  title: 'OBiCare - Obstetric Intelligence Care',
  description: 'Advanced obstetric intelligence and maternal health monitoring platform',
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
