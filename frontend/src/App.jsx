
// import Dictaphone from "./assests/SpeechRecognition";
import './index.css';

import React from "react";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import { useState, useEffect } from "react";
import emailjs from "@emailjs/browser";
import { motion } from "framer-motion";

const Dictaphone = () => {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  const [currentStep, setCurrentStep] = useState(0);
  const initialGraph = [
    "Step 1: Open your email client",
    "Step 2: Click on 'Compose' or 'New Email'",
    "Step 3: Enter the recipient's email address",
    "Step 4: Enter a subject for the email",
    "Step 5: Write your message in the email body",
    "Step 6: Click on 'Send' to send the email",
  ];
  console.log(initialGraph);

  const [formatedText, setFormatedText] = useState(true);

  const [graph, setGraph] = useState(initialGraph);
  const [text, setText] = useState("");
  const [graphVal, setGraphVal] = useState(false)

  // useEffect(() => {
  //   const timer = setInterval(() => {
  //     setCurrentStep((prevStep) =>
  //       prevStep < graph.length - 1 ? prevStep + 1 : prevStep
  //     );
  //   }, 3000); // Change the interval to 10 seconds

  //   return () => clearInterval(timer); // cleanup on unmount
  // }, [graph]);

  const [isAutomating, setIsAutomating] = useState(false);
  const [reqType, setReqType] = useState(0);

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  const abort = async () => {
    const abortResponse = await fetch("http://0.0.0.0:8000/abort");
    const abortReply = await abortResponse.json();
    console.log(abortReply);
    setIsAutomating(!isAutomating);
    resetTranscript();
    setGraph([]);
  };

  const handleRecordSubmit = async () => {
    SpeechRecognition.stopListening();
    setIsAutomating(true);
    console.log(transcript);

    const message = transcript !== "" ? transcript : text;

    try {
      const response = await fetch("http://0.0.0.0:8000/transcript", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      });


      if (!response.ok) {
        console.log(response);
        throw new Error("Network response was not ok");
      }

      const data = await response.json(); // Parse response body as JSON
      setReqType(data.req);

      console.log("THE STEPS ARE : ", JSON.parse(data.steps));

        const steps = JSON.parse(data.steps);
        console.log("STEPS : ", steps);
        console.log("HEEEELLLLL");
        for (let i = 0; i < steps.length; i++) {
          console.log("i am working");
          console.log(steps[i]);
        }

        const stepsArray = Object.values(steps);
        console.log(stepsArray);
        
        setGraph(stepsArray);
        setFormatedText(Array.isArray(stepsArray));
        setGraphVal(true);

      if (data.req == 1) {

        setTimeout(async () => {
          const response2 = await fetch("http://0.0.0.0:8000/sendmail", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: message }),
          });
          if (!response2.ok) {
            console.log(response2);
            throw new Error("Network response was not ok");
          }
          const data2 = await response2.json(); // Parse response body as JSON
          console.log("Success:", data2);
          console.log("json : ", data2.jsonres);
          console.log(data2.jsonres.email);
          console.log(data2.jsonres.body);
          console.log(data2.jsonres.subject);
          console.log(data2.jsonres.sender_name);
          console.log(data2.jsonres.receiver_name);
          const jsonData = JSON.parse(data2.jsonres);
          console.log(jsonData.email);
          console.log(jsonData.body);
          console.log(jsonData.subject);
          console.log(jsonData.sender_name);
          console.log(jsonData.receiver_name);
          emailjs
            .send(
              "service_3jzzrvd",
              "template_8omipe5",
              {
                to_name: jsonData.receiver_name,
                message: jsonData.body,
                from_name: jsonData.sender_name,
                subject: jsonData.subject,
                reciever_email: jsonData.email,
              },
              {
                publicKey: "T-uXJUetQw84JsASr",
              }
            )
            .then(
              () => {
                console.log("SUCCESS!");
              },
              (error) => {
                console.log("FAILED...", error.text);
              }
            );
        }, 5000);
      }
      if (data.req == 2) {
        console.log(JSON.parse(data.steps));

        const steps = JSON.parse(data.steps);
        for (let i = 0; i < steps.length; i++) {
          console.log(steps[i]);
        }

        const stepsArray = Object.values(steps);
        console.log(stepsArray);
        setGraph(stepsArray);

        const response2 = await fetch("http://0.0.0.0:8000/fetchmail", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: message }),
        });
        if (!response2.ok) {
          console.log(response2);
          throw new Error("Network response was not ok");
        }
        const data2 = await response2.json(); // Parse response body as JSON

        console.log("RESULT 2 : ", data2.res);
      }
      console.log("Success:", data);
      setIsAutomating(true);
    } catch (error) {
      console.error("Error:", error);
      setIsAutomating(false);
    }
  };

  return (
    <div className="text-center flex flex-col">
      {!isAutomating ? (
        <div>
          <div className="flex justify-center text-center">
            {listening ? (
              <button
                className="flex justify-center rounded-full"
                onClick={SpeechRecognition.stopListening}
              >
                <img
                  height="200px"
                  width="200px"
                  className="bg-red-700 hover:bg-red-500 animate-pulse rounded-full p-8"
                  src="images/mic.svg"
                  alt="mic"
                />
              </button>
            ) : (
              <button
                className="flex rounded-full justify-center"
                onClick={() => {
                  SpeechRecognition.startListening({ continuous: true });
                  console.log("mic on to kiya h bhai");
                }}
              >
                <img
                  className="bg-blue-400 transition-transform hover:bg-blue-300  rounded-full p-8"
                  height="200px"
                  width="200px"
                  src="images/mic.svg"
                  alt="mic"
                />
              </button>
            )}
          </div>
          <h3 className="p-10 mx-auto flex-1 text-center text-xl font-mono font-semibold">
            {transcript}..
            <br/>
            <br/>
            <input
              className="bg-[#eeeded] text-black"
              value={text}
              onChange={(e) => {
                setText(e.target.value);
              }}
            />
            {listening ? <span>..</span> : <span></span>}
          </h3>
          {(transcript !== "" || text !== "") && (
            <button
              onClick={handleRecordSubmit}
              className="bg-blue-400 text-xl font-bold hover:bg-[#eeeded] transition-transform hover:text-blue-400 rounded-lg m-5 p-4 w-fit h-fit mx-auto px-6"
            >
              Automate
            </button>
          )}
        </div>
      ) : (
        <div className="bg-black min-h-screen w-screen absolute top-0 left-0 ">
          <div className="flex justify-end items-center p-2 cursor-pointer">
            <button onClick={abort} className="h-30 w-30 flex items-center">
              <h3 className="font-mono font-semibold text-xl animate-none">
                Stop Automation
              </h3>
              <img
                className="h-10 w-10 p-2 hover:animate-spin"
                src="images/cross.svg"
              />
            </button>
          </div>
          {reqType === 0 && (
            <div>
              <div className="flex justify-center items-center">
                <h1 className="text-4xl font-bold text-white">
                  Automating your commands
                </h1>
                <img
                  className="h-16 w-16 p-2 animate-spin"
                  src="images/loadingAutomate.svg"
                />
              </div>
            </div>
          )}
          {reqType === 1 && <div>mail commands automation</div>}
          {reqType === 2 && (
            <div>
              Fetch desired mails
              <div>
                mails fetch on the terminal
                {/* {graph && (
                <div className="flex text-center flex-col overflow-y-auto">
                  {graph.map((steps, index) => (
                    <div
                      className="flex flex-col justify-center items-center"
                      key={index}
                    >
                      <motion.div
                        className="mx-auto bg-gradient-to-br from-pink-500 to-pink-600 text-2xl font-mono font-semibold rounded-lg flex justify-center items-center px-10 py-8"
                        initial={{ scale: 0 }}
                        animate={{ rotate: 360, scale: 1 }}
                        transition={{
                          type: "spring",
                          stiffness: 260,
                          damping: 20,
                        }}
                      >
                        {steps}
                      </motion.div>
                      {index < currentStep && (
                        <motion.div className="h-20 w-20">
                          <img src="images/downArrow.svg" alt="down-arrow" />
                        </motion.div>
                      )}
                    </div>
                  ))}
                </div>
              )} */}
              </div>
            </div>
          )}
          {reqType === 3 && <div>Database automation</div>}
          <div className="flex text-center flex-col overflow-y-auto">
            {(graphVal && graph && graph.length>0 && formatedText) ? (graph[0].map((step, index) => (
              <div
                className="flex flex-col justify-center items-center"
                key={index}
              >
                <motion.div
                  className="mx-auto bg-gradient-to-br from-pink-500 to-pink-600 text-2xl font-mono font-semibold rounded-lg flex  justify-center items-center px-10 py-8"
                  initial={{ scale: 0 }}
                  animate={{ rotate: 360, scale: 1 }}
                  transition={{
                    type: "spring",
                    stiffness: 260,
                    damping: 20,
                  }}
                >
                  {step}
                </motion.div>
                {index < graph[0].length-1 && (
                  <motion.div className="h-20 w-20">
                    <img src="images/downArrow.svg" alt="down-arrow" />
                  </motion.div>
                )}
              </div>
            ))):<div><h2 className="bg-red-500">Graph couldnt be processed</h2></div>}
          </div>

          {/* {graph && (
                <div className="flex text-center flex-col overflow-y-auto">
                  {graph.map((steps, index) => (
                    <div
                      className="flex flex-col justify-center items-center"
                      key={index}
                    >
                      <motion.div
                        className="mx-auto bg-gradient-to-br from-pink-500 to-pink-600 text-2xl font-mono font-semibold rounded-lg flex justify-center items-center px-10 py-8"
                        initial={{ scale: 0 }}
                        animate={{ rotate: 360, scale: 1 }}
                        transition={{
                          type: "spring",
                          stiffness: 260,
                          damping: 20,
                        }}
                      >
                        {steps}
                      </motion.div>
                      {index < currentStep && (
                        <motion.div className="h-20 w-20">
                          <img src="images/downArrow.svg" alt="down-arrow" />
                        </motion.div>
                      )}
                    </div>
                  ))}
                </div>
              )} */}
          {/* {Array.isArray(graph) && graph.length > 0 && (
            <div className="flex text-center flex-col overflow-y-auto">
              {graph.map((step, index) => (
                <div
                  className="flex flex-col justify-center items-center"
                  key={index}
                >
                  <motion.div
                    className="mx-auto bg-gradient-to-br from-pink-500 to-pink-600 text-2xl font-mono font-semibold rounded-lg flex justify-center items-center px-10 py-8"
                    initial={{ scale: 0 }}
                    animate={{ rotate: 360, scale: 1 }}
                    transition={{
                      type: "spring",
                      stiffness: 260,
                      damping: 20,
                    }}
                  >
                    {step}
                  </motion.div>
                  {index < currentStep && (
                    <motion.div className="h-20 w-20">
                      <img src="images/downArrow.svg" alt="down-arrow" />
                    </motion.div>
                  )}
                </div>
              ))}
            </div>
          )} */}
        </div>
      )}
    </div>
  );
};


function App() {

  return (
    <div className="h-screen">
      <header className=" text-white flex text-4xl p-5 font-extrabold font-mono from-neutral-100">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          className="w-10 h-10"
          xmlns="http://www.w3.org/2000/svg"
          stroke="#ffffff"
          transform="matrix(1, 0, 0, 1, 0, 0)rotate(0)"
        >
          <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke="#CCCCCC"
            stroke-width="0.72"
          ></g>
          <g id="SVGRepo_iconCarrier">
            {" "}
            <path
              d="M3 8H5M7 5.85714V5.5C7 4.11929 8.11929 3 9.5 3C10.8807 3 12 4.11929 12 5.5C12 6.88071 10.8807 8 9.5 8H8"
              stroke="#eeeded"
              stroke-width="1.752"
              stroke-linecap="round"
            ></path>{" "}
            <path
              d="M4 14H5M15 17V17.5C15 19.433 16.567 21 18.5 21C20.433 21 22 19.433 22 17.5C22 15.567 20.433 14 18.5 14H9"
              stroke="#eeeded"
              stroke-width="1.752"
              stroke-linecap="round"
            ></path>{" "}
            <path
              d="M2 11H8M15 8V7.5C15 5.567 16.567 4 18.5 4C20.433 4 22 5.567 22 7.5C22 9.433 20.433 11 18.5 11H12.25"
              stroke="#eeeded"
              stroke-width="1.752"
              stroke-linecap="round"
            ></path>{" "}
          </g>
        </svg>
        <h1 className="px-3">Breeze</h1>
      </header>
      <div className="flex p-5 justify-center">
        <div className="text-2xl text-gray-300 font-mono font-bold text-center">
          <h2 className="p-3">
            <span className="text-blue-300">Your wish, our command!</span>
          </h2>
          <p className="p-3 text-3xl">
            Experience Seamless Automation with Just Your Voice!
          </p>
        </div>
      </div>
      <div className="p-5 flex justify-center">
        {/* <RecorderHooks /> */}
        <Dictaphone/>
      </div>
    </div>
  );
}

export default App;
