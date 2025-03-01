"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";

export default function ResearchInterests() {
  const [curVal, setCurVal] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  return (
    <>
      <Label>Current Interests</Label>
      {interests.map((interest, i) => (
        <div key={interest} className='flex flex-row gap-x-2'>
          <Input defaultValue={interest} name='current-interests' />
          <Button
            variant='destructive'
            className='cursor-pointer'
            onClick={() => setInterests(v => v.toSpliced(i, 1))}>
            Delete
          </Button>
        </div>
      ))}
      <div className='flex flex-row gap-x-2'>
        <Input
          value={curVal}
          name='current-interests'
          onChange={e => setCurVal(e.currentTarget.value)}
          placeholder='What are you interested in?'
        />
        <Button
          type='button'
          className='cursor-pointer'
          variant='outline'
          onClick={() => {
            if (curVal.trim() === "") {
              return;
            }
            setInterests(v =>
              v.filter(x => x !== curVal).concat(curVal.trim())
            );
            setCurVal("");
          }}
          value={curVal}>
          Add
        </Button>
      </div>
    </>
  );
}
