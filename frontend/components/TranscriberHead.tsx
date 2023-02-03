import Head from "next/head";

export const TranscriberHead = ({ title }: { title: string }) => {
  return (
    <Head>
      <title>{title}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <link rel="icon" href="/favicon.ico" />
      <link rel="stylesheet" href="https://unpkg.com/mvp.css@1.12/mvp.css" />
    </Head>
  );
};
