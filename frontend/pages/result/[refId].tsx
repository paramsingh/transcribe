import { getDetailsForToken } from "../../client/api-client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import {
  Text,
  Alert,
  AlertIcon,
  Box,
  Button,
  Heading,
  Link,
  Spinner,
} from "@chakra-ui/react";
import { Transcription } from "../../components/Transcription";
import { YoutubeEmbed } from "../../components/YoutubeEmbed";
import { TranscriberHead } from "../../components/TranscriberHead";
import { LogoAndTitle } from "../../components/LogoAndTitle";

enum DataType {
  TRANSCRIPTION = "TRANSCRIPTION",
  IMPROVEMENT = "IMPROVEMENT",
}

export default function TranscriptionResult() {
  const [transcriptionResult, setTranscriptionResult] = useState<any>(null); // TODO: type this
  const [improvement, setImprovement] = useState<string>("");
  const [waiting, setWaiting] = useState<boolean>(true);
  const [showData, setShowData] = useState<DataType>(DataType.TRANSCRIPTION);
  const [summary, setSummary] = useState<string>("");
  const [link, setLink] = useState<string>("");
  const router = useRouter();
  const refId = router.query.refId as string;

  useEffect(() => {
    if (waiting && refId) {
      getDetailsForToken(refId).then((data) => {
        if (data["result"]) {
          setLink(data["link"]);
          setTranscriptionResult(JSON.parse(data["result"]));
          setImprovement(data["improvement"]);
          setSummary(data["summary"]);
          setWaiting(false);
        }
      });
    }
  }, [refId, waiting]);

  useEffect(() => {
    if (improvement) {
      setShowData(DataType.IMPROVEMENT);
    }
  }, [improvement]);

  return (
    <>
      <TranscriberHead title={`Transcribe ${link && `| ${link}`}`} />
      <main>
        <LogoAndTitle />
        <section>
          {/*<header><h2>{refId}</h2></header>*/}
          {waiting && <Spinner />}
          {!waiting && !transcriptionResult && (
            <Box paddingTop={10} paddingBottom={10}>
              <Heading as={"h5"}>
                Transcription is non-existent or still in progress!
              </Heading>
            </Box>
          )}
          {/*** TODO: think about hiding this entirely */}
          {!waiting && transcriptionResult && !improvement && (
            <Alert status="info" style={{ marginBottom: "20px" }}>
              <AlertIcon />
              We&lsquo;re working on improving this transcription. Please check
              again later.
            </Alert>
          )}
          {!waiting && transcriptionResult && improvement && (
            <Alert status="success" style={{ marginBottom: "20px" }}>
              {showData == DataType.IMPROVEMENT ? (
                <Text>
                  This is a GPT-3 enhanced version of the transcription ✨.
                  Click{" "}
                  <Link onClick={() => setShowData(DataType.TRANSCRIPTION)}>
                    here
                  </Link>{" "}
                  to see the original.
                </Text>
              ) : (
                <Text>
                  There is an improved ✨ version of this transcription
                  available. Click{" "}
                  <Link onClick={() => setShowData(DataType.IMPROVEMENT)}>
                    here
                  </Link>{" "}
                  to see it.
                </Text>
              )}
            </Alert>
          )}
          {!waiting && link && <YoutubeEmbed link={link} />}
          {!waiting && summary && (
            <Transcription text={summary} heading="Summary" />
          )}
          {!waiting &&
            transcriptionResult &&
            showData == DataType.TRANSCRIPTION && (
              <Transcription
                heading="Transcription"
                text={transcriptionResult.transcription}
              />
            )}
          <br />
          {!waiting && improvement && showData == DataType.IMPROVEMENT && (
            <Transcription text={improvement} heading="Transcription" />
          )}
        </section>
      </main>
    </>
  );
}
