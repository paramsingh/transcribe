import { Box, Button, Divider, Heading, Input, Text } from "@chakra-ui/react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { getAnswer, getDetailsForToken } from "../../client/api-client";
import { LogoAndTitle } from "../../components/LogoAndTitle";
import { TranscriberHead } from "../../components/TranscriberHead";
import { YoutubeEmbed } from "../../components/YoutubeEmbed";

type Source = {
  transcription_token: string;
  video: string;
};

export default function TranscriptionAsk() {
  const [question, setQuestion] = useState<string>("");
  const [answer, setAnswer] = useState<string>("");
  const [waiting, setWaiting] = useState<boolean>(false);
  const [sources, setSources] = useState<Source[]>([]);

  const submit = () => {
    setWaiting(true);
    getAnswer("yc", question).then((data) => {
      setAnswer(data.answer);
      setSources(data.sources);
      setWaiting(false);
    });
  };

  return (
    <>
      <TranscriberHead
        title={"Transcriber | AskYC"}
        description={`AskYC: Ask the YCombinator Youtube channel anything.`}
      />
      <main>
        <LogoAndTitle title="Transcriber / AskYC" />
        <Text>
          We transcribed the{" "}
          <Link href="https://www.youtube.com/@ycombinator">
            YCombinator YouTube channel
          </Link>{" "}
          and created a bot that can answer questions based on the videos. Ask
          it a question!{" "}
        </Text>
        <Text marginTop={5}>
          If you have any feedback, please reach out to{" "}
          <Link href="https://twitter.com/iliekcomputers">@iliekcomputers</Link>{" "}
          on Twitter.
        </Text>
        <Heading as="h2" size="2xl" marginTop={5} marginBottom={5}>
          Ask a question
        </Heading>
        <Input
          size="lg"
          placeholder="Enter your question"
          marginBottom={5}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={waiting}
        />
        <Button
          colorScheme={"blue"}
          onClick={submit}
          isLoading={waiting}
          loadingText={"Getting an answer"}
        >
          Ask
        </Button>
        {answer !== "" && (
          <Box marginTop={5} marginBottom={5}>
            <Heading size="lg" marginBottom={5}>
              Answer
            </Heading>
            <Text>{answer}</Text>
          </Box>
        )}
        {sources &&
          sources.map((src) => {
            return (
              <>
                <Heading as="h3" fontSize={"3xl"} marginBottom={5}>
                  Source
                </Heading>
                <Text marginBottom={5}>
                  We got this answer from this{" "}
                  <Link href={src.video}>video</Link>. Here&apos;s a{" "}
                  <Link href={`/result/${src.transcription_token}`}>
                    link to the transcription
                  </Link>
                  . If you want to ask questions about this particular video,
                  you can go to{" "}
                  <Link href={`/ask/${src.transcription_token}`}>
                    the ask page for the video
                  </Link>
                  .
                </Text>
                <YoutubeEmbed link={src.video} />
              </>
            );
          })}
      </main>
    </>
  );
}
