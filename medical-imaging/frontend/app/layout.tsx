import './globals.css'

export const metadata = {
  title: 'Medical Imaging AI - DICOM & AI Analysis',
  description: 'Advanced dicom & ai analysis platform',
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
