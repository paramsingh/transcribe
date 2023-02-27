import { Spinner } from "@chakra-ui/react";
import { TranscriberHead } from "./TranscriberHead";

export const LoadingPage = () => {
  return (
    <>
      <TranscriberHead title="Transcriber | Loading" description="loading" />
      <main>
        <Spinner />
      </main>
    </>
  );
};
