import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

function FlowDiagram() {
  const graph = [
    "Step1",
    "Step2",
    "Step3",
    "Step4",
    "Step5",
    "Step6",
    "Step7",
    "Step8",
    "Step9",
    "Step10",
  ];

  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prevStep) =>
        prevStep < graph.length - 1 ? prevStep + 1 : prevStep
      );
    }, 2000);

    return () => clearInterval(timer); // cleanup on unmount
  }, [graph]);

  return (
    <div className="flex text-center flex-col overflow-y-auto">
      {graph.slice(0, currentStep + 1).map((step, index) => (
        <div className="flex flex-col justify-center items-center" key={index}>
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
  );
}

export default FlowDiagram;
