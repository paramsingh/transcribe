import Link from "next/link";
import { Flex, Heading } from "@chakra-ui/react";
import Image from "next/image";
import scriber from "../public/scriber.png";

export const LogoAndTitle = () => {
  return (
    <Flex direction="row" paddingBottom={10} alignItems="center">
      <Link href="/">
        <Image
          src={scriber}
          alt="scriber"
          style={{ maxHeight: "100px", maxWidth: "100px" }}
        />
      </Link>
      <Heading as={"h1"} size="3xl" paddingLeft={10}>
        <Link href="/" style={{ textDecoration: "none" }}>
          Transcriber
        </Link>
      </Heading>
    </Flex>
  );
};
