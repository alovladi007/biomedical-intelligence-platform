export const metadata = {
  title: 'MYNX NatalCare - Maternal Health Monitoring',
  description: 'Advanced maternal health monitoring platform',
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
