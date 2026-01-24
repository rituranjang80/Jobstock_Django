import { Plus_Jakarta_Sans } from 'next/font/google'
import '../../node_modules/bootstrap/dist/css/bootstrap.css'
import './assets/css/styles.css'
import './assets/css/colors.css'
import { Metadata } from 'next'

const JakartaSans = Plus_Jakarta_Sans({
  weight: ['200','300','400','500','600','700','800'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
   variable: '--font-JakartaSans',
  display: 'swap',
})

export const metadata: Metadata = {
  title: "Reetch - Next Ts Job Listing, Job Portal Landing & Admin Dashboard Template",
  description: "Reetch - Next Ts Job Listing, Job Portal Landing & Admin Dashboard Template"
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
     <html lang="en" className={`${JakartaSans.variable}`}>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossOrigin="anonymous"></script>
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
