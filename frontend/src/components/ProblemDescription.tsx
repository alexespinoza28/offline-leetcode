import React from "react";
import styled from "styled-components";
import { Problem, DIFFICULTY_COLORS } from "../types";

const Container = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #1a1a1a;
  margin: 4px 8px 8px 8px;
  border-radius: 8px;
  min-height: 0;
`;

const Header = styled.div`
  margin-bottom: 16px;
`;

const Title = styled.h2`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #d4d4d4;
`;

const Meta = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const DifficultyBadge = styled.span<{ $difficulty: string }>`
  color: ${(props) =>
    DIFFICULTY_COLORS[props.$difficulty as keyof typeof DIFFICULTY_COLORS]};
  font-weight: 500;
  font-size: 14px;
`;

const TagList = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
`;

const Tag = styled.span`
  background-color: #3e3e3e;
  color: #888;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
`;

const Statement = styled.div`
  line-height: 1.6;
  margin-bottom: 20px;

  p {
    margin-bottom: 12px;
  }

  code {
    background-color: #2d2d2d;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 13px;
  }

  pre {
    background-color: #2d2d2d;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 12px 0;

    code {
      background: none;
      padding: 0;
    }
  }
`;

const Section = styled.div`
  margin-bottom: 20px;
`;

const SectionTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #d4d4d4;
`;

const ExampleContainer = styled.div`
  background-color: #2d2d2d;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
`;

const ExampleLabel = styled.div`
  font-weight: 600;
  margin-bottom: 8px;
  color: #d4d4d4;
`;

const ExampleContent = styled.pre`
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  font-size: 13px;
  margin: 0;
  white-space: pre-wrap;
  color: #d4d4d4;
`;

const ConstraintList = styled.ul`
  list-style: none;
  padding: 0;

  li {
    margin-bottom: 6px;
    padding-left: 16px;
    position: relative;

    &:before {
      content: "•";
      position: absolute;
      left: 0;
      color: #888;
    }
  }
`;

interface ProblemDescriptionProps {
  problem: Problem;
}

const ProblemDescription: React.FC<ProblemDescriptionProps> = ({ problem }) => {
  // Simple markdown-to-HTML conversion for basic formatting
  const formatStatement = (markdown: string) => {
    return markdown
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .split("\n\n")
      .map((paragraph) => `<p>${paragraph.replace(/\n/g, "<br>")}</p>`)
      .join("");
  };

  return (
    <Container>
      <Header>
        <Title>{problem.title}</Title>
        <Meta>
          <DifficultyBadge $difficulty={problem.difficulty}>
            {problem.difficulty}
          </DifficultyBadge>
          <TagList>
            {problem.tags.map((tag) => (
              <Tag key={tag}>{tag}</Tag>
            ))}
          </TagList>
        </Meta>
      </Header>

      <Statement
        dangerouslySetInnerHTML={{
          __html: formatStatement(problem.statement_md),
        }}
      />

      {problem.examples.length > 0 && (
        <Section>
          <SectionTitle>Examples</SectionTitle>
          {problem.examples.map((example, index) => (
            <ExampleContainer key={index}>
              <ExampleLabel>Example {index + 1}:</ExampleLabel>
              <div>
                <strong>Input:</strong>
                <ExampleContent>{example.in}</ExampleContent>
              </div>
              <div>
                <strong>Output:</strong>
                <ExampleContent>{example.out}</ExampleContent>
              </div>
            </ExampleContainer>
          ))}
        </Section>
      )}

      {problem.constraints.length > 0 && (
        <Section>
          <SectionTitle>Constraints</SectionTitle>
          <ConstraintList>
            {problem.constraints.map((constraint, index) => (
              <li key={index}>
                <strong>{constraint.name}:</strong> {constraint.desc}
                {constraint.min !== undefined &&
                  constraint.max !== undefined && (
                    <span>
                      {" "}
                      ({constraint.min} ≤ {constraint.name} ≤ {constraint.max})
                    </span>
                  )}
                {constraint.value && <span> = {constraint.value}</span>}
              </li>
            ))}
          </ConstraintList>
        </Section>
      )}
    </Container>
  );
};

export default ProblemDescription;
