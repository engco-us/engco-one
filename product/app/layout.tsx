import './globals.css';
import type { Metadata, Viewport } from 'next';
import { SWRConfig } from 'swr';

export const metadata: Metadata = {
  title: 'ENGCO ONE',
  description: 'A governed AI operations workspace for project teams.'
};

export const viewport: Viewport = {
  maximumScale: 1
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className="bg-white text-black dark:bg-gray-950 dark:text-white"
    >
      <body className="min-h-[100dvh] bg-gray-50">
        <SWRConfig value={{}}>{children}</SWRConfig>
      </body>
    </html>
  );
}
