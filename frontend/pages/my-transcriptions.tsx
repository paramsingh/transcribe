import { useState, useEffect } from "react";
import { getSessionToken } from "../utils/sessionTokenUtils";
import { getUser } from "../utils/getUser";
import { getTranscriptionsForUser } from "../client/api-client";
import { TranscriberHead } from "../components/TranscriberHead";
import { LogoAndTitle } from "../components/LogoAndTitle";
import { Heading, Spinner } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { TranscriptionTable } from "../components/TranscriptionTable";
export default function MyTranscriptions() {
  const [user, setUser] = useState<any>(null);
  const [transcriptions, setTranscriptions] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();

  useEffect(() => {
    const sessionToken = getSessionToken();
    if (!sessionToken) {
      return;
    }
    getUser(sessionToken)
      .then((user) => {
        setUser(user);
      })
      .catch((err) => {
        alert("You must be signed in to view this page");
        router.push("/login");
      });
  }, []);

  useEffect(() => {
    if (!user) return;
    getTranscriptionsForUser(user.token)
      .then((data) => {
        setTranscriptions(data.transcriptions);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
      });
  }, [user]);

  return (
    <>
      <TranscriberHead title={"Transcriber | Your transcriptions"} />
      <main>
        <LogoAndTitle />
        <Heading as="h1" size="xl" paddingBottom={10}>
          Your transcriptions
        </Heading>
        {loading && <Spinner size="lg" marginLeft={"50%"} />}
        {!loading && <TranscriptionTable transcriptions={transcriptions} />}
      </main>
    </>
  );
}
