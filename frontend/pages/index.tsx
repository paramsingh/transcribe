import { useEffect, useState } from "react";
import Head from "next/head";
import Image from "next/image";
import { Inter } from "@next/font/google";
import {
  Spinner,
  Box,
  Heading,
  Input,
  Button,
  Flex,
  IconButton,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverHeader,
  Portal,
} from "@chakra-ui/react";
import InfoIcon from "@chakra-ui/icon";
import styles from "../styles/Home.module.css";
import { getDetailsForUUID, submitLink } from "../client/api-client";
import { validateUrl } from "../utils/validateUrl";
import { useRouter } from "next/router";
import scriber from "../public/scriber.png";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export default function Transcription() {
  const [link, setLink] = useState<string>("");
  const [transcriptionID, setTranscriptionID] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [listenID, setListenID] = useState<any>(null); // TODO: type this
  const [waiting, setWaiting] = useState<boolean>(true);
  const { push } = useRouter();

  const listenForResults = (id: string) => {
    console.debug("listening for results");
    if (!id) return;
    console.debug("have uuid");
    console.debug("sending request");
    getDetailsForUUID(id).then((data) => {
      if (data["result"]) {
        console.debug("have data", data);
        console.debug("listen ID", listenID);
        setWaiting(false);
        push(`/result/${id}`);
      }
    });
  };

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
      <Head>
        <title>Transcriber</title>
        {/*<meta name="description" content="Generated by create next app" />*/}
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="https://unpkg.com/mvp.css@1.12/mvp.css" />
      </Head>
      <main>
        <div>
          <Flex direction="row" paddingBottom={10} alignItems="center">
            <Image
              src={scriber}
              alt="scriber"
              style={{ maxHeight: "100px", maxWidth: "100px" }}
            />
            <Heading as={"h1"} size="3xl" paddingLeft={10}>
              Transcriber
            </Heading>
          </Flex>

          <Heading as={"h2"} size="md" paddingBottom={10}>
            Transcribe your favorite YouTube videos using the magic of AI.
          </Heading>
          <Box paddingBottom={10}>
            <Input
              size="lg"
              onChange={(e) => setLink(e.target.value)}
              disabled={submitted}
              placeholder={"Enter a YouTube link for us to transcribe."}
            />
          </Box>
          <Box paddingBottom={200}>
            <Button
              colorScheme={"blue"}
              onClick={(e) => submit()}
              isLoading={submitted}
              loadingText={"Transcribing"}
            >
              Submit
            </Button>
            {submitted && (
              <Popover>
                <PopoverTrigger>
                  <IconButton
                    icon={<InfoIcon />}
                    aria-label="info"
                    marginLeft={2}
                  />
                </PopoverTrigger>
                <Portal>
                  <PopoverContent>
                    <PopoverArrow />
                    <PopoverCloseButton />
                    <PopoverHeader>Note</PopoverHeader>
                    <PopoverBody>
                      We will redirect you to the transcription when it is
                      ready, it may take some time. If you do not want to wait,
                      come back to{" "}
                      <Link href={`/result/${transcriptionID}`}>this link</Link>{" "}
                      later and we should have it ready.
                    </PopoverBody>
                  </PopoverContent>
                </Portal>
              </Popover>
            )}
          </Box>
        </div>
      </main>
    </>
  );
}
