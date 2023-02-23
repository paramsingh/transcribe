import { useEffect, useState } from "react";
import { Inter } from "@next/font/google";
import { Box, Heading, Input, Button, Text, Divider } from "@chakra-ui/react";
import { getDetailsForToken, submitLink } from "../client/api-client";
import { validateUrl } from "../utils/validateUrl";
import { useRouter } from "next/router";
import { LogoAndTitle } from "../components/LogoAndTitle";
import { TranscriberHead } from "../components/TranscriberHead";
import { getUser } from "../utils/getUser";
import { getSessionToken } from "../utils/sessionTokenUtils";
import { CopyLink } from "../components/CopyLink";
import { PopoverInfo } from "../components/PopoverInfo";
import Link from "next/link";
import { RecentTranscriptions } from "../components/RecentTranscriptions";

const inter = Inter({ subsets: ["latin"] });

export default function Transcription() {
  const [link, setLink] = useState<string>("");
  const [transcriptionID, setTranscriptionID] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [listenID, setListenID] = useState<any>(null); // TODO: type this
  const [waiting, setWaiting] = useState<boolean>(true);
  const [user, setUser] = useState<any>(null);
  const { push } = useRouter();

  const listenForResults = (id: string) => {
    console.debug("listening for results");
    if (!id) return;
    getDetailsForToken(id).then((data) => {
      if (data["result"]) {
        setWaiting(false);
        push(`/result/${id}`);
      }
    });
  };

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
        console.error(err);
      });
  }, []);

  useEffect(() => {
    if (!waiting) {
      clearInterval(listenID);
    }
  }, [waiting, listenID]);

  const submit = () => {
    if (!validateUrl(link)) {
      alert("not a youtube link, try again!");
      return;
    }

    setSubmitted(true);
    submitLink(link).then((data) => {
      console.debug("submitted successfully!", data);
      console.debug(data.id);
      setTranscriptionID(data.id);
      const id = setInterval(() => {
        listenForResults(data.id);
      }, 5 * 1000);
      setListenID(id);
    });
  };

  return (
    <>
      <TranscriberHead
        title={"Transcriber"}
        description={"Transcribe Youtube videos with the help of AI."}
      />
      <main>
        <div>
          <LogoAndTitle />
          {user ? (
            <>
              <Text fontSize="xl" paddingBottom={5}>
                Welcome, {user.email}! You can{" "}
                <Link href="/logout">sign out here.</Link> See your previous
                transcriptions <Link href="/my-transcriptions">here.</Link>
              </Text>
            </>
          ) : (
            <Text fontSize="xl" paddingBottom={5}>
              Welcome! <Link href="/login">Sign in</Link> to keep track of
              things you&apos;ve transcribed.
            </Text>
          )}
          <Heading as={"h2"} size="md" paddingBottom={5}>
            Transcribe your favorite YouTube videos using the magic of AI.
          </Heading>
          <Box paddingBottom={5}>
            <Input
              size="lg"
              onChange={(e) => setLink(e.target.value)}
              disabled={submitted}
              placeholder={"Enter a YouTube link for us to transcribe."}
            />
          </Box>
          <Box marginBottom={5}>
            <Button
              colorScheme={"blue"}
              onClick={(e) => submit()}
              isLoading={submitted}
              loadingText={"Transcribing"}
              marginBottom={5}
            >
              Submit
            </Button>
            {submitted && (
              <>
                <PopoverInfo transcriptionID={transcriptionID} />
                <CopyLink
                  link={`https://transcribe.param.codes/result/${transcriptionID}`}
                />
              </>
            )}
            <Divider marginBottom={5} />
            <RecentTranscriptions />
          </Box>
          <Divider marginBottom={5} />
          <Box>
            <Heading as={"h2"} size="lg" paddingBottom={5}>
              Come talk to me!
            </Heading>
            If this seems like something you&lsquo;d find useful or you try it
            out, please reach out to me on Twitter, as I&lsquo;d love to talk:{" "}
            <Link href="https://twitter.com/iliekcomputers">
              @iliekcomputers
            </Link>
          </Box>
        </div>
      </main>
    </>
  );
}
