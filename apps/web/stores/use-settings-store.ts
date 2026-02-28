"use client";

import { create } from "zustand";

interface SettingsState {
  values: Record<string, unknown>;
  setValues: (values: Record<string, unknown>) => void;
  patchValue: (key: string, value: unknown) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  values: {},
  setValues: (values) => set({ values }),
  patchValue: (key, value) =>
    set((state) => ({
      values: {
        ...state.values,
        [key]: value
      }
    }))
}));
