import React, { useState, useEffect } from 'react';
import { User, Bot, Sparkles, Mic, Volume2, Settings, Plus, Trash2 } from 'lucide-react';

const AgentSelector = ({ agents, onAgentsChange, availableVoices }) => {
  const [editingAgentId, setEditingAgentId] = useState(null);
  const [newAgent, setNewAgent] = useState({
    name: '',
    role: 'explainer',
    personality: '',
    voice_id: availableVoices?.[0]?.voice_id || ''
  });

  // Default agent configurations
  const defaultAgents = [
    {
      id: 'explainer',
      name: 'Dr. Knowledge',
      role: 'explainer',
      personality: 'Expert in the subject matter, patient, and thorough in explanations',
      voice_id: '21m00Tcm4TlvDq8ikWAM'
    },
    {
      id: 'curious',
      name: 'Curious Carl',
      role: 'curious',
      personality: 'Inquisitive, asks insightful questions, represents the audience\'s perspective',
      voice_id: 'AZCnJ6YX1Dv9e0J9z4Jm'
    },
    {
      id: 'user',
      name: 'You',
      role: 'user',
      personality: 'The actual user who can ask questions during the conversation',
      voice_id: 'EXAVITQu4vr4xnSDxMaL'
    }
  ];

  // Initialize with default agents if none provided
  useEffect(() => {
    if (!agents || agents.length === 0) {
      onAgentsChange(defaultAgents);
    }
  }, []);

  const handleAgentChange = (id, field, value) => {
    const updatedAgents = agents.map(agent =>
      agent.id === id ? { ...agent, [field]: value } : agent
    );
    onAgentsChange(updatedAgents);
  };

  const handleAddAgent = () => {
    if (!newAgent.name || !newAgent.personality) return;

    const agentToAdd = {
      ...newAgent,
      id: `agent-${Date.now()}`
    };

    onAgentsChange([...agents, agentToAdd]);

    // Reset new agent form
    setNewAgent({
      name: '',
      role: 'explainer',
      personality: '',
      voice_id: availableVoices?.[0]?.voice_id || ''
    });
  };

  const handleRemoveAgent = (id) => {
    // Don't allow removing the user agent or if only 2 agents remain
    if (id === 'user' || agents.length <= 2) return;

    const updatedAgents = agents.filter(agent => agent.id !== id);
    onAgentsChange(updatedAgents);
  };

  const getRoleIcon = (role) => {
    const icons = {
      'explainer': Bot,
      'curious': Sparkles,
      'user': User
    };
    return icons[role] || Bot;
  };

  const getRoleColor = (role) => {
    const colors = {
      'explainer': 'bg-blue-100 text-blue-600',
      'curious': 'bg-purple-100 text-purple-600',
      'user': 'bg-green-100 text-green-600'
    };
    return colors[role] || 'bg-gray-100 text-gray-600';
  };

  return (
    <div className="agent-selector bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <h3 className="text-lg font-bold text-gray-800 flex items-center">
          <Settings className="mr-2 text-gray-600" size={20} />
          Podcast Agents Configuration
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Configure the agents that will participate in the podcast conversation
        </p>
      </div>

      <div className="p-4 space-y-4">
        {agents?.map((agent) => (
          <div
            key={agent.id}
            className={`agent-card p-4 rounded-lg border transition-all ${
              editingAgentId === agent.id
                ? 'border-blue-300 bg-blue-50'
                : 'border-gray-200 bg-white hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${getRoleColor(agent.role)}`}>
                  {React.createElement(getRoleIcon(agent.role), { size: 20 })}
                </div>

                <div className="flex-1 min-w-0">
                  {editingAgentId === agent.id ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={agent.name}
                        onChange={(e) => handleAgentChange(agent.id, 'name', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Agent name"
                      />

                      <select
                        value={agent.role}
                        onChange={(e) => handleAgentChange(agent.id, 'role', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="explainer">Explainer</option>
                        <option value="curious">Curious</option>
                        <option value="user">User</option>
                      </select>

                      <textarea
                        value={agent.personality}
                        onChange={(e) => handleAgentChange(agent.id, 'personality', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[80px]"
                        placeholder="Agent personality and behavior"
                      />

                      <select
                        value={agent.voice_id}
                        onChange={(e) => handleAgentChange(agent.id, 'voice_id', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {availableVoices?.map((voice) => (
                          <option key={voice.voice_id} value={voice.voice_id}>
                            {voice.name} ({voice.category})
                          </option>
                        ))}
                      </select>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="font-semibold text-gray-800">{agent.name}</h4>
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600 capitalize">
                          {agent.role}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{agent.personality}</p>
                      <div className="flex items-center space-x-2 mt-2 text-xs text-gray-500">
                        <Mic size={12} />
                        <span>
                          {availableVoices?.find(v => v.voice_id === agent.voice_id)?.name || 'Default Voice'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-col space-y-2 ml-3">
                {editingAgentId === agent.id ? (
                  <button
                    onClick={() => setEditingAgentId(null)}
                    className="p-1 text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="Save changes"
                  >
                    <Check size={18} />
                  </button>
                ) : (
                  <button
                    onClick={() => setEditingAgentId(agent.id)}
                    className="p-1 text-gray-600 hover:bg-gray-100 rounded-lg"
                    title="Edit agent"
                  >
                    <Settings size={18} />
                  </button>
                )}

                {agent.id !== 'user' && (
                  <button
                    onClick={() => handleRemoveAgent(agent.id)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded-lg"
                    title="Remove agent"
                    disabled={agents.length <= 2}
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add new agent form */}
      <div className="p-4 border-t border-gray-100 bg-gray-50">
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
          <Plus className="mr-2 text-gray-600" size={16} />
          Add New Agent
        </h4>

        <div className="space-y-3">
          <input
            type="text"
            value={newAgent.name}
            onChange={(e) => setNewAgent({...newAgent, name: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Agent name (e.g., Dr. Science)"
          />

          <select
            value={newAgent.role}
            onChange={(e) => setNewAgent({...newAgent, role: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="explainer">Explainer</option>
            <option value="curious">Curious</option>
          </select>

          <textarea
            value={newAgent.personality}
            onChange={(e) => setNewAgent({...newAgent, personality: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[80px]"
            placeholder="Describe the agent's personality and behavior"
          />

          <select
            value={newAgent.voice_id}
            onChange={(e) => setNewAgent({...newAgent, voice_id: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {availableVoices?.map((voice) => (
              <option key={voice.voice_id} value={voice.voice_id}>
                {voice.name} ({voice.category})
              </option>
            ))}
          </select>

          <button
            onClick={handleAddAgent}
            disabled={!newAgent.name || !newAgent.personality}
            className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:bg-green-200 disabled:cursor-not-allowed"
          >
            <Plus className="inline mr-2" size={16} />
            Add Agent
          </button>
        </div>
      </div>

      <div className="p-4 border-t border-gray-100 bg-gray-50 text-sm text-gray-600">
        <div className="flex items-start space-x-2">
          <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <Bot size={12} className="text-blue-600" />
          </div>
          <div>
            <p className="font-medium text-gray-800">Agent Roles:</p>
            <ul className="mt-1 space-y-1">
              <li className="flex items-start">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                <span><strong>Explainer:</strong> Provides expert knowledge and detailed explanations</span>
              </li>
              <li className="flex items-start">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                <span><strong>Curious:</strong> Asks insightful questions and represents the audience</span>
              </li>
              <li className="flex items-start">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                <span><strong>User:</strong> Represents you - can ask follow-up questions during the conversation</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentSelector;
