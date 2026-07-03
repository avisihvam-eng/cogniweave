"use client";

import { useEffect, useState } from "react";
import { 
  Network, 
  HelpCircle, 
  ExternalLink, 
  BookOpen, 
  TrendingUp, 
  Brain,
  Link2,
  RefreshCw,
  Search
} from "lucide-react";

interface GraphNode {
  id: string;
  label: string;
  description: string;
  doc_id?: string;
  x: number;
  y: number;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export default function GraphPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchGraphData = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/graph");
      if (res.ok) {
        const data = await res.json();
        
        // Give random coordinate offsets for layout if not present
        const mappedNodes = data.nodes.map((node: any, idx: number) => {
          const angles = [0, 60, 120, 180, 240, 300];
          const angle = (angles[idx % angles.length] * Math.PI) / 180;
          const radius = idx === 0 ? 0 : 150 + Math.floor(idx / angles.length) * 50;
          return {
            ...node,
            x: 350 + radius * Math.cos(angle),
            y: 250 + radius * Math.sin(angle)
          };
        });
        
        setNodes(mappedNodes);
        setEdges(data.edges);
      } else {
        throw new Error("Failed to fetch");
      }
    } catch (err) {
      console.warn("Backend API not reachable. Mocking Knowledge Graph data.");
      
      // Fallback Mock Graph
      const mockNodes: GraphNode[] = [
        { id: "n1", label: "Compounding Knowledge", description: "Information structured to build compounding returns over years.", x: 350, y: 250 },
        { id: "n2", label: "Second-Order Thinking", description: "Analyzing the downstream consequences of immediate choices.", x: 200, y: 150 },
        { id: "n3", label: "Permissionless Leverage", description: "Writing code, producing media, and building products to scale impact without permission.", x: 500, y: 150 },
        { id: "n4", label: "Spaced Repetition", description: "Reviewing surafced insights at increasing intervals to improve long-term retention.", x: 220, y: 350 },
        { id: "n5", label: "Incentive Alignment", description: "Aligning reward metrics with long-term retention and customer satisfaction.", x: 480, y: 350 },
        { id: "n6", label: "Charlie Munger Principles", description: "Latticework of mental models to reduce decision-making blindspots.", x: 350, y: 80 }
      ];

      const mockEdges: GraphEdge[] = [
        { id: "e1", source: "n1", target: "n2", label: "supports" },
        { id: "e2", source: "n1", target: "n3", label: "expands" },
        { id: "e3", source: "n1", target: "n4", label: "built_upon" },
        { id: "e4", source: "n2", target: "n6", label: "inspired_by" },
        { id: "e5", source: "n3", target: "n5", label: "related_to" },
        { id: "e6", source: "n4", target: "n6", label: "related_to" }
      ];

      setNodes(mockNodes);
      setEdges(mockEdges);
      setSelectedNode(mockNodes[0]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, []);

  const filteredNodes = nodes.filter(node => 
    node.label.toLowerCase().includes(searchQuery.toLowerCase()) || 
    node.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getAdjacentEdges = (nodeId: string) => {
    return edges.filter(e => e.source === nodeId || e.target === nodeId);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#060609]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-[#8b5cf6] animate-spin" />
          <p className="text-sm text-gray-400">Loading Knowledge Connections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex h-screen overflow-hidden">
      {/* Visual Canvas Area */}
      <div className="flex-1 p-6 flex flex-col relative h-full bg-[#060609]">
        {/* Header toolbar */}
        <div className="flex justify-between items-center z-10">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Network className="w-6 h-6 text-[#8b5cf6]" />
              Personal Knowledge Graph
            </h1>
            <p className="text-xs text-gray-400 mt-0.5">
              Visualizing how separate notes connect semantically. Click nodes to trace links.
            </p>
          </div>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-2 text-gray-500 w-4 h-4" />
              <input
                type="text"
                placeholder="Find node..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.05)] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#8b5cf6]"
              />
            </div>
            <button 
              onClick={fetchGraphData}
              className="p-2 rounded-lg glass-panel text-gray-400 hover:text-white"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Dynamic SVG network visualizer */}
        <div className="flex-1 relative mt-4 border border-[rgba(255,255,255,0.03)] bg-[#07070b] rounded-2xl overflow-hidden glow-purple">
          <svg className="w-full h-full cursor-grab">
            {/* Draw edge lines */}
            {edges.map((edge) => {
              const srcNode = nodes.find(n => n.id === edge.source);
              const tgtNode = nodes.find(n => n.id === edge.target);
              if (!srcNode || !tgtNode) return null;
              
              const isSelected = selectedNode && (selectedNode.id === edge.source || selectedNode.id === edge.target);
              
              return (
                <g key={edge.id}>
                  <line
                    x1={srcNode.x}
                    y1={srcNode.y}
                    x2={tgtNode.x}
                    y2={tgtNode.y}
                    stroke={isSelected ? "#8b5cf6" : "#2e2e42"}
                    strokeWidth={isSelected ? 2 : 1}
                    strokeDasharray={isSelected ? "none" : "3,3"}
                    className="transition-all duration-300"
                  />
                  {/* Label background */}
                  <rect
                    x={(srcNode.x + tgtNode.x) / 2 - 25}
                    y={(srcNode.y + tgtNode.y) / 2 - 8}
                    width={50}
                    height={16}
                    fill="#07070b"
                    rx={4}
                  />
                  {/* Relationship label */}
                  <text
                    x={(srcNode.x + tgtNode.x) / 2}
                    y={(srcNode.y + tgtNode.y) / 2 + 4}
                    fill={isSelected ? "#a78bfa" : "#6b7280"}
                    fontSize={9}
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {edge.label}
                  </text>
                </g>
              );
            })}

            {/* Draw node circles */}
            {filteredNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const matchesSearch = searchQuery && node.label.toLowerCase().includes(searchQuery.toLowerCase());
              
              return (
                <g 
                  key={node.id} 
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(node)}
                  className="cursor-pointer group"
                >
                  {/* Glow underlay */}
                  <circle
                    r={isSelected ? 28 : 22}
                    fill={isSelected ? "url(#purpleGlow)" : "transparent"}
                    className="transition-all duration-300"
                  />
                  {/* Base Circle */}
                  <circle
                    r={isSelected ? 18 : 14}
                    fill={isSelected ? "#8b5cf6" : matchesSearch ? "#06b6d4" : "#1c1c28"}
                    stroke={isSelected ? "#a78bfa" : matchesSearch ? "#22d3ee" : "rgba(255,255,255,0.08)"}
                    strokeWidth={2}
                    className="transition-all duration-300 group-hover:scale-110"
                  />
                  {/* Text label underneath */}
                  <text
                    y={32}
                    fill={isSelected ? "#ffffff" : "#d1d5db"}
                    fontSize={10}
                    fontWeight={isSelected ? "bold" : "normal"}
                    textAnchor="middle"
                    className="select-none pointer-events-none transition-colors duration-300"
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}

            {/* SVG Defs for gradients */}
            <defs>
              <radialGradient id="purpleGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
              </radialGradient>
            </defs>
          </svg>
        </div>
      </div>

      {/* Details Side Panel */}
      <aside className="w-80 border-l border-[rgba(255,255,255,0.05)] bg-[#09090d] p-6 flex flex-col h-full overflow-y-auto">
        {selectedNode ? (
          <div className="space-y-6 flex-1 flex flex-col justify-between">
            <div className="space-y-6">
              {/* Icon / Title */}
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-xl bg-[rgba(139,92,246,0.1)] border border-[rgba(139,92,246,0.2)] flex items-center justify-center">
                  <Brain className="w-5 h-5 text-[#8b5cf6]" />
                </div>
                <h2 className="text-lg font-bold text-white leading-tight">{selectedNode.label}</h2>
                <span className="text-[10px] font-bold text-[#06b6d4] bg-[rgba(6,182,212,0.1)] border border-[rgba(6,182,212,0.2)] px-2 py-0.5 rounded uppercase">
                  Active Concept
                </span>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Semantic Meaning</span>
                <p className="text-xs text-gray-300 leading-relaxed bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.03)] p-3 rounded-lg">
                  {selectedNode.description}
                </p>
              </div>

              {/* Relations list */}
              <div className="space-y-3">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Connected Nodes</span>
                <div className="space-y-2">
                  {getAdjacentEdges(selectedNode.id).map((edge) => {
                    const otherNodeId = edge.source === selectedNode.id ? edge.target : edge.source;
                    const otherNode = nodes.find(n => n.id === otherNodeId);
                    if (!otherNode) return null;
                    return (
                      <button
                        key={edge.id}
                        onClick={() => setSelectedNode(otherNode)}
                        className="w-full text-left bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.04)] border border-[rgba(255,255,255,0.03)] p-2.5 rounded-lg flex items-center justify-between text-xs transition-colors duration-200"
                      >
                        <div>
                          <span className="font-semibold text-white block">{otherNode.label}</span>
                          <span className="text-[10px] text-gray-400 block capitalize mt-0.5">relation: {edge.label}</span>
                        </div>
                        <Link2 className="w-3.5 h-3.5 text-gray-500" />
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Document reference link */}
            <div className="border-t border-[rgba(255,255,255,0.04)] pt-6 mt-6">
              <a
                href="#"
                className="w-full py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                Go to Source Document <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center text-gray-500 space-y-2">
            <HelpCircle className="w-8 h-8 text-gray-600" />
            <p className="text-xs font-medium">Select a concept node in the network to inspect its semantic connections.</p>
          </div>
        )}
      </aside>
    </div>
  );
}
