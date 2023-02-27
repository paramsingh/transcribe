import {
  Spinner,
  Heading,
  Alert,
  AlertIcon,
  Text,
  Link,
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { getDetailsForToken } from "../client/api-client";
import { LogoAndTitle } from "./LogoAndTitle";
import { TranscriberHead } from "./TranscriberHead";
import { Transcription } from "./Transcription";
import { YoutubeEmbed } from "./YoutubeEmbed";

export enum DataType {
  TRANSCRIPTION = "TRANSCRIPTION",
  IMPROVEMENT = "IMPROVEMENT",
}

export const TranscriptionResult = ({
  transcriptionID,
}: {
  transcriptionID: string;
}) => {
  const [transcriptionResult, setTranscriptionResult] = useState<any>(null); // TODO: type this
  const [improvement, setImprovement] = useState<string>("");
  const [waiting, setWaiting] = useState<boolean>(true);
  const [showData, setShowData] = useState<DataType>(DataType.TRANSCRIPTION);
  const [summary, setSummary] = useState<string>("");
  const [link, setLink] = useState<string>("");
  const [intervalID, setIntervalID] = useState<any>(null);
  const [transcriptionInProgress, setTranscriptionInProgress] =
    useState<boolean>(false);

  useEffect(() => {
    const getTranscriptionDetails = () => {
      getDetailsForToken(transcriptionID)
        .then((data) => {
          if (data["result"]) {
            setTranscriptionInProgress(false);
            setLink(data["link"]);
            setTranscriptionResult(JSON.parse(data["result"]));
            setImprovement(data["improvement"]);
            setSummary(data["summary"]);
            setWaiting(false);
          } else {
            setTranscriptionInProgress(true);
          }
        })
        .catch((e) => {
          setWaiting(false);
          if (intervalID) {
            clearInterval(intervalID);
          }
        });
    };

    if (waiting && transcriptionID) {
      if (intervalID) return;
      getTranscriptionDetails();
      const id = setInterval(getTranscriptionDetails, 30 * 1000);
      setIntervalID(id);
    }
  }, [transcriptionID, waiting, intervalID]);

  useEffect(() => {
    if (improvement) {
      setShowData(DataType.IMPROVEMENT);
      clearInterval(intervalID);
    }
  }, [improvement, intervalID]);

  return (
    <>
      <TranscriberHead
        title={`Transcribe ${link && `| ${link}`}`}
        description={`A transcription and summary of the youtube video with link: ${link}`}
      />
      <main>
        <LogoAndTitle />
        <section>
          {waiting && (
            <>
              <Spinner />
              {transcriptionInProgress ? (
                <Text fontSize={"xl"}>
                  This transcription is still in progress. Please come back
                  later (or leave this page open and we will update it
                  automatically!).
                </Text>
              ) : (
                <Text fontSize="xl">Getting your transcription...</Text>
              )}
            </>
          )}
          {!waiting && !transcriptionResult && (
            <Heading as={"h5"} size={"md"}>
              Transcription does not exist. {":("}
            </Heading>
          )}
          {/*** TODO: think about hiding this entirely */}
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
          {/* Youtube embed */}
          {!waiting && link && <YoutubeEmbed link={link} />}
          {/* Summary */}
          {!waiting && summary && (
            <Transcription text={summary} heading="Summary" />
          )}
          {/* show the result if not improved */}
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
};
