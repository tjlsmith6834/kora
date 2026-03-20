import React from "react";
import "./rubricTableCriteriaList.css";
import SmallButton from "../smallButton/smallButton";

interface RubricTableCriteriaListProps {
  criteria: string[];
  editable: boolean;
  onChange: (newList: string[]) => void;
}

export default function RubricTableCriteriaList({
  criteria,
  editable,
  onChange,
}: RubricTableCriteriaListProps) {

  const handleUpdate = (idx: number, val: string) => {
    const next = [...criteria];
    next[idx] = val;
    onChange(next);
  };
  const handleAdd = () => onChange([...criteria, ""]);
  const handleRemove = (idx: number) =>
    onChange(criteria.filter((_, i) => i !== idx));

  return (
    <ul className="criteria-list">

        {criteria.map((c, i) => (
          <li key={i}>
            {editable ? (
                <div className="criteria-row">
                  <>
                    <input
                        value={c}
                        onChange={(e) => handleUpdate(i, e.target.value)}
                    />
                    <SmallButton
                      onClick={() => handleRemove(i)}
                      variant={"secondary"}
                      symbol={true}
                    >
                      x
                    </SmallButton>
                  </>
                </div>
                  ) : (
                  <span>{c}</span>
                  )}
                </li>
            ))}
            {editable && (
              <li>
                <SmallButton
                  onClick={handleAdd}
                  variant={"tertiary"}
                  noBorder={false}
                >
                  + Add Criterion
                </SmallButton>
              </li>
            )}
    </ul>
  );
}