import React from 'react';
import { Card, CardContent } from "../../../components/ui/card";
import { BitNetOmegaPanel } from "./bitnetOmegaPanel";
import { HiveMindPanel } from "./hiveMindPanel";
import { PhoenixPanel } from "./phoenixPanel";
import { GenesisPanel } from "./genesisPanel";
import { SwarmNexusPanel } from "./swarmNexusPanel";
import { DreamscapePanel } from "./dreamscapePanel";
import { FortressPanel } from "./fortressPanel";
import { QuantumLeapPanel } from "./quantumLeapPanel";
import { FreeEnergyPanel } from "./freeEnergyPanel";
import { PerpetualMotionPanel } from "./perpetualMotionPanel";

export const OmegaDashboard = () => {
  return (
    <div className="space-y-6 p-6">
      <header className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
          LEO AI V43 -- OMEGA
        </h1>
        <p className="text-xl text-gray-500 mt-2">
          "The Irrelevance Engine -- Making GPUs Unnecessary"
        </p>
        <div className="mt-4 inline-flex items-center px-4 py-2 bg-green-100 rounded-full">
          <span className="text-green-800 font-bold">
            [TROPHY] 100% Competitive vs NVIDIA -- In Our Game
          </span>
        </div>
      </header>
      
      <div className="grid grid-cols-2 gap-6">
        <BitNetOmegaPanel />
        <HiveMindPanel />
        <PhoenixPanel />
        <GenesisPanel />
        <SwarmNexusPanel />
        <DreamscapePanel />
        <FortressPanel />
        <QuantumLeapPanel />
        <FreeEnergyPanel />
        <PerpetualMotionPanel />
      </div>
      
      <Card className="border-2 border-green-500 bg-green-950 mt-6">
        <CardContent className="p-6">
          <h2 className="text-2xl font-bold text-center text-green-400 mb-4">
            The Final Score
          </h2>
          <div className="grid grid-cols-3 gap-8 text-center">
            <div>
              <p className="text-5xl font-bold text-green-500">100%</p>
              <p className="text-gray-300 font-semibold mt-2">In Our Game</p>
              <p className="text-sm text-gray-500">Intelligence per Watt per Dollar</p>
            </div>
            <div>
              <p className="text-5xl font-bold text-blue-500">Infinity</p>
              <p className="text-gray-300 font-semibold mt-2">Cost Advantage</p>
              <p className="text-sm text-gray-500">$0 vs $190,000</p>
            </div>
            <div>
              <p className="text-5xl font-bold text-purple-500">Unbounded</p>
              <p className="text-gray-300 font-semibold mt-2">Innovation</p>
              <p className="text-sm text-gray-500">Algorithms vs Physics</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
