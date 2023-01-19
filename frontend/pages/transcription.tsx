import { useEffect, useState } from "react";
import Head from "next/head";
import Image from "next/image";
import { Inter } from "@next/font/google";
import { Spinner, Box, Heading, Input, Button, Text } from "@chakra-ui/react";
import styles from "../styles/Home.module.css";
import { getDetailsForUUID, submitLink } from "../client/api-client";
import { validateUrl } from "../utils/validateUrl";
import { NextRequest, NextResponse } from "next/server";

const inter = Inter({ subsets: ["latin"] });

export default function Transcription() {
  const [link, setLink] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [listenID, setListenID] = useState<any>(null); // TODO: type this
  const [result, setResult] = useState<any>(null); // TODO: type this

  const listenForResults = (id: string, request: NextRequest) => {
    console.debug("listening for results");
    if (!id) return;
    console.debug("have uuid");
    console.debug("sending request");
    getDetailsForUUID(id).then((data) => {
      if (data["result"]) {
        console.debug("have data", data);
        console.debug("listen ID", listenID);
        setResult(JSON.parse(data["result"]));
        const url = request.nextUrl.clone()

        NextResponse.redirect("/result/" + id);
      }
    });
  };

  useEffect(() => {
    if (result) {
      console.debug("clearing interval");
      clearInterval(listenID);
    }
  }, [result, listenID]);

  const submit = () => {
    setResult(null);
    if (!validateUrl(link)) {
      alert("not a youtube link, try again!");
      return;
    }

    setSubmitted(true);
    submitLink(link).then((data) => {
      console.debug("submitted successfully!", data);
      console.debug(data.id);
      const id = setInterval(() => {
        listenForResults(data.id);
      }, 5 * 1000);
      setListenID(id);
    });
  };

  return (
    <>
      <Head>
        <title>transcribe</title>
        {/*<meta name="description" content="Generated by create next app" />*/}
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="https://unpkg.com/mvp.css@1.12/mvp.css" />
      </Head>
      <main>
        <div>
          <Heading as={"h1"} size="3xl">
            Youtube link
          </Heading>
          <Box paddingTop={10} paddingBottom={10}>
            <Heading as={"h5"}>Enter a link for us to transcribe.</Heading>
          </Box>
          <Box paddingBottom={10}>
            <Input size="lg" onChange={(e) => setLink(e.target.value)} />
          </Box>
          <Button colorScheme={"blue"} onClick={(e) => submit()}>
            Submit
          </Button>
          {submitted && !result && (
            <Box paddingTop={10}>
              <Text fontSize="2xl">Please wait for a transcription</Text>
              <Spinner />
            </Box>
          )}
          {result && (
            <Box paddingTop={10}>
              <Heading as={"h3"} size="xl">
                Transcription
              </Heading>
              <Text paddingTop={4}>{result.transcription}</Text>
            </Box>
          )}
        </div>
      </main>
    </>
  );
}
