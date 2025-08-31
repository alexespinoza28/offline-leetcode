import React, { useState, useMemo } from "react";
import styled from "styled-components";
import { Problem, DIFFICULTY_COLORS } from "../types";

const Container = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1a1a1a;
  margin: 8px;
  margin-bottom: 4px;
  border-radius: 8px;
  overflow: hidden;
  min-height: 0;
`;

const Header = styled.div`
  padding: 16px;
  border-bottom: 1px solid #404040;
  font-weight: 600;
  font-size: 14px;
  background-color: #1e1e1e;
  color: #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const FilterSection = styled.div`
  padding: 16px;
  border-bottom: 1px solid #404040;
  background-color: #1a1a1a;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 10px 14px;
  background-color: #1a1a1a;
  border: 1px solid #404040;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 13px;
  margin-bottom: 12px;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #ffa116;
    box-shadow: 0 0 0 2px rgba(255, 161, 22, 0.1);
    background-color: #1e1e1e;
  }

  &::placeholder {
    color: #6b7280;
  }
`;

const FilterRow = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const FilterSelect = styled.select`
  padding: 6px 12px;
  background-color: #1a1a1a;
  border: 1px solid #404040;
  border-radius: 6px;
  color: #e8e8e8;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #ffa116;
    box-shadow: 0 0 0 2px rgba(255, 161, 22, 0.1);
  }

  &:hover {
    border-color: #525252;
  }
`;

const ProblemList = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const ProblemItem = styled.div<{ isSelected: boolean }>`
  padding: 14px 16px;
  margin: 4px 8px;
  cursor: pointer;
  border-radius: 8px;
  background-color: ${(props) =>
    props.isSelected ? "rgba(255, 161, 22, 0.1)" : "transparent"};
  border: 1px solid
    ${(props) => (props.isSelected ? "rgba(255, 161, 22, 0.3)" : "transparent")};
  transition: all 0.2s ease;

  &:hover {
    background-color: ${(props) =>
      props.isSelected
        ? "rgba(255, 161, 22, 0.15)"
        : "rgba(255, 255, 255, 0.05)"};
    border-color: ${(props) =>
      props.isSelected
        ? "rgba(255, 161, 22, 0.4)"
        : "rgba(255, 255, 255, 0.1)"};
  }
`;

const ProblemTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #e8e8e8;
  line-height: 1.3;
`;

const ProblemMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  margin-bottom: 6px;
`;

const DifficultyBadge = styled.span<{ $difficulty: string }>`
  color: ${(props) =>
    DIFFICULTY_COLORS[props.$difficulty as keyof typeof DIFFICULTY_COLORS]};
  font-weight: 600;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background-color: ${(props) => {
    const color =
      DIFFICULTY_COLORS[props.$difficulty as keyof typeof DIFFICULTY_COLORS];
    return `${color}20`;
  }};
`;

const TagList = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
`;

const Tag = styled.span`
  background-color: rgba(255, 255, 255, 0.08);
  color: #9ca3af;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.12);
    color: #d1d5db;
  }
`;

const EmptyState = styled.div`
  padding: 32px 16px;
  text-align: center;
  color: #888;
  font-size: 14px;
`;

interface ProblemListProps {
  problems: Problem[];
  selectedProblem: Problem | null;
  onProblemSelect: (problem: Problem) => void;
  connectionStatus?: any;
  onReconnect?: () => void;
}

const ProblemListComponent: React.FC<ProblemListProps> = ({
  problems,
  selectedProblem,
  onProblemSelect,
  connectionStatus,
  onReconnect,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [difficultyFilter, setDifficultyFilter] = useState("All");
  const [sortBy, setSortBy] = useState("title");

  // Get unique tags for filtering
  const allTags = useMemo(() => {
    const tagSet = new Set<string>();
    problems.forEach((problem) => {
      problem.tags.forEach((tag) => tagSet.add(tag));
    });
    return Array.from(tagSet).sort();
  }, [problems]);

  // Filter and sort problems
  const filteredProblems = useMemo(() => {
    let filtered = problems.filter((problem) => {
      const matchesSearch =
        problem.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        problem.slug.toLowerCase().includes(searchTerm.toLowerCase()) ||
        problem.tags.some((tag) =>
          tag.toLowerCase().includes(searchTerm.toLowerCase())
        );

      const matchesDifficulty =
        difficultyFilter === "All" || problem.difficulty === difficultyFilter;

      return matchesSearch && matchesDifficulty;
    });

    // Sort problems
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "difficulty":
          const difficultyOrder = { Easy: 1, Medium: 2, Hard: 3 };
          return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
        case "title":
        default:
          return a.title.localeCompare(b.title);
      }
    });

    return filtered;
  }, [problems, searchTerm, difficultyFilter, sortBy]);

  if (problems.length === 0) {
    return (
      <Container>
        <Header>Problems</Header>
        <EmptyState>
          No problems available.
          <br />
          Check your backend connection.
        </EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <span>
          Problems ({filteredProblems.length}/{problems.length})
        </span>
        {connectionStatus && (
          <div
            style={{
              fontSize: "11px",
              color: connectionStatus.connected ? "#10b981" : "#ef4444",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <div
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: connectionStatus.connected
                  ? "#10b981"
                  : "#ef4444",
              }}
            ></div>
            {connectionStatus.connected ? "Online" : "Offline"}
          </div>
        )}
      </Header>

      <FilterSection>
        <SearchInput
          type="text"
          placeholder="Search problems, tags..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FilterRow>
          <FilterSelect
            value={difficultyFilter}
            onChange={(e) => setDifficultyFilter(e.target.value)}
          >
            <option value="All">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </FilterSelect>
          <FilterSelect
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="title">Sort by Title</option>
            <option value="difficulty">Sort by Difficulty</option>
          </FilterSelect>
        </FilterRow>
      </FilterSection>

      <ProblemList>
        {filteredProblems.length === 0 ? (
          <EmptyState>
            No problems match your filters.
            <br />
            Try adjusting your search or filters.
          </EmptyState>
        ) : (
          filteredProblems.map((problem) => (
            <ProblemItem
              key={problem.slug}
              isSelected={selectedProblem?.slug === problem.slug}
              onClick={() => onProblemSelect(problem)}
            >
              <ProblemTitle>{problem.title}</ProblemTitle>
              <ProblemMeta>
                <DifficultyBadge $difficulty={problem.difficulty}>
                  {problem.difficulty}
                </DifficultyBadge>
                <span>•</span>
                <span>{problem.slug}</span>
              </ProblemMeta>
              {problem.tags.length > 0 && (
                <TagList>
                  {problem.tags.slice(0, 3).map((tag) => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                  {problem.tags.length > 3 && (
                    <Tag>+{problem.tags.length - 3}</Tag>
                  )}
                </TagList>
              )}
            </ProblemItem>
          ))
        )}
      </ProblemList>
    </Container>
  );
};

export default ProblemListComponent;
