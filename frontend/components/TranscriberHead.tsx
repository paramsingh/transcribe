import Head from "next/head";

export const TranscriberHead = ({
  title,
  description,
}: {
  title: string;
  description: string;
}) => {
  return (
    <Head>
      <title>{title}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="description" content={description} />
      <link rel="icon" href="/favicon.ico" />
      <link rel="stylesheet" href="https://unpkg.com/mvp.css@1.12/mvp.css" />
    </Head>
  );
};
