import './globals.css'

export const metadata = {
  title: 'BioTensor Labs - MLOps & Model Management',
  description: 'Advanced mlops & model management platform',
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
