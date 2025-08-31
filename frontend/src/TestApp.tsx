import React from "react";
import styled from "styled-components";

const Container = styled.div`
  display: flex;
  height: 100vh;
  background-color: #0f0f0f;
  color: #e8e8e8;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen",
    "Ubuntu", "Cantarell", sans-serif;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 20px;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #ffa116;
`;

const Message = styled.p`
  font-size: 16px;
  text-align: center;
  max-width: 600px;
  line-height: 1.5;
`;

const Button = styled.button`
  background-color: #0e639c;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #1177bb;
  }
`;

function TestApp() {
  const handleClick = () => {
    alert("Frontend is working! 🎉");
  };

  return (
    <Container>
      <Title>Interview Coding Platform</Title>
      <Message>
        Welcome to the Interview Coding Platform! This is a test page to verify
        that the frontend is working correctly. If you can see this message,
        React, TypeScript, and styled-components are all functioning properly.
      </Message>
      <Button onClick={handleClick}>Test Interaction</Button>
      <div style={{ fontSize: "14px", color: "#888" }}>
        Frontend Status: ✅ Working
      </div>
    </Container>
  );
}

export default TestApp;
