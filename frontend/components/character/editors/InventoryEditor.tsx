/**
 * Inventory Editor
 * 
 * Full CRUD editor for equipped items and backpack inventory
 */

'use client'

import { useState } from 'react'

interface InventoryItem {
  name: string
  quantity: number
  weight?: number
  description?: string
  [key: string]: any
}

interface InventoryData {
  equipped_items?: Record<string, InventoryItem[]>
  backpack?: InventoryItem[]
  currency?: {
    copper?: number
    silver?: number
    electrum?: number
    gold?: number
    platinum?: number
  }
  [key: string]: any
}

interface InventoryEditorProps {
  data: InventoryData | null
  onSave: (data: InventoryData) => void
}

const EQUIPMENT_SLOTS = [
  'head', 'eyes', 'neck', 'chest', 'back', 'wrist', 
  'hands', 'ring', 'waist', 'legs', 'feet', 'main_hand', 'off_hand'
]

export function InventoryEditor({ data, onSave }: InventoryEditorProps) {
  const [inventory, setInventory] = useState<InventoryData>(() => {
    const initial = data || {
      equipped_items: {},
      backpack: [],
    }
    
    // Ensure equipped_items is initialized as empty dict if needed
    if (!initial.equipped_items || Object.keys(initial.equipped_items).length === 0) {
      initial.equipped_items = {}
    }
    
    // Ensure backpack is an array
    if (!Array.isArray(initial.backpack)) {
      initial.backpack = []
    }
    
    return initial
  })
  const [isSaving, setIsSaving] = useState(false)
  const [editingItem, setEditingItem] = useState<{ type: 'equipped' | 'backpack', index: number, slot?: string } | null>(null)
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(inventory)
    } finally {
      setIsSaving(false)
    }
  }
  
  // Backpack operations
  const addBackpackItem = () => {
    const newItem: InventoryItem = { name: 'New Item', quantity: 1, weight: 0, description: '' }
    setInventory({
      ...inventory,
      backpack: [...(inventory.backpack || []), newItem]
    })
  }
  
  const removeBackpackItem = (index: number) => {
    setInventory({
      ...inventory,
      backpack: inventory.backpack?.filter((_, i) => i !== index) || []
    })
  }
  
  const updateBackpackItem = (index: number, field: string, value: any) => {
    const updated = [...(inventory.backpack || [])]
    updated[index] = { ...updated[index], [field]: value }
    setInventory({ ...inventory, backpack: updated })
  }
  
  // Equipped items operations
  const addEquippedItem = (slot: string) => {
    const newItem: InventoryItem = { name: 'New Equipment', quantity: 1, weight: 0 }
    const slotItems = inventory.equipped_items?.[slot] || []
    setInventory({
      ...inventory,
      equipped_items: {
        ...inventory.equipped_items,
        [slot]: [...slotItems, newItem]
      }
    })
  }
  
  const removeEquippedItem = (slot: string, index: number) => {
    const slotItems = inventory.equipped_items?.[slot] || []
    setInventory({
      ...inventory,
      equipped_items: {
        ...inventory.equipped_items,
        [slot]: slotItems.filter((_, i) => i !== index)
      }
    })
  }
  
  const updateEquippedItem = (slot: string, index: number, field: string, value: any) => {
    const slotItems = [...(inventory.equipped_items?.[slot] || [])]
    slotItems[index] = { ...slotItems[index], [field]: value }
    setInventory({
      ...inventory,
      equipped_items: {
        ...inventory.equipped_items,
        [slot]: slotItems
      }
    })
  }
  
  // Move item from backpack to equipped slot
  const moveToEquipped = (backpackIndex: number, targetSlot: string) => {
    const item = inventory.backpack?.[backpackIndex]
    if (!item) return
    
    const newBackpack = inventory.backpack?.filter((_, i) => i !== backpackIndex) || []
    const slotItems = inventory.equipped_items?.[targetSlot] || []
    
    setInventory({
      ...inventory,
      backpack: newBackpack,
      equipped_items: {
        ...inventory.equipped_items,
        [targetSlot]: [...slotItems, item]
      }
    })
  }
  
  // Move item from equipped slot to backpack
  const moveToBackpack = (slot: string, itemIndex: number) => {
    const item = inventory.equipped_items?.[slot]?.[itemIndex]
    if (!item) return
    
    const slotItems = inventory.equipped_items?.[slot]?.filter((_, i) => i !== itemIndex) || []
    
    setInventory({
      ...inventory,
      backpack: [...(inventory.backpack || []), item],
      equipped_items: {
        ...inventory.equipped_items,
        [slot]: slotItems
      }
    })
  }
  
  const totalWeight = () => {
    let total = 0
    inventory.backpack?.forEach(item => {
      const weight = item.definition?.weight || item.weight || 0
      total += weight * item.quantity
    })
    Object.values(inventory.equipped_items || {}).forEach(slotItems => {
      slotItems.forEach(item => {
        const weight = item.definition?.weight || item.weight || 0
        total += weight * item.quantity
      })
    })
    return total.toFixed(1)
  }
  
  return (
    <div className="space-y-6">
      {/* Info Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm text-blue-800">
          ℹ️ <strong>Item Management:</strong> Inventory data is imported from D&D Beyond. You can adjust quantities and move items between backpack and equipped slots.
        </p>
      </div>
      
      {/* Equipped Items */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
          <span>🛡️</span> Equipped Items
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          {/* Show actual equipped items from data */}
          {Object.keys(inventory.equipped_items || {}).length > 0 ? (
            Object.entries(inventory.equipped_items || {}).map(([slot, slotItems]) => (
              <div key={slot} className="bg-white border border-gray-200 rounded-lg p-3">
                <div className="flex items-center mb-2">
                  <span className="text-sm font-bold text-gray-700 capitalize">
                    {slot.replace('_', ' ')}
                  </span>
                </div>
                
                {slotItems.length === 0 ? (
                  <p className="text-xs text-gray-500 italic">Empty slot</p>
                ) : (
                  <div className="space-y-2">
                    {slotItems.map((item, index) => (
                      <div key={index} className="bg-gray-50 rounded p-2">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <input
                            type="text"
                            value={item.definition?.name || item.name || ''}
                            readOnly
                            className="flex-1 text-sm px-2 py-1 border border-gray-200 rounded bg-gray-50"
                            title="Item data is read-only"
                          />
                          <button
                            onClick={() => moveToBackpack(slot, index)}
                            className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
                            title="Move to backpack"
                          >
                            🎒
                          </button>
                        </div>
                        <div className="flex gap-2">
                          <input
                            type="number"
                            value={item.definition?.weight || item.weight || 0}
                            readOnly
                            className="w-20 text-xs px-2 py-1 border border-gray-200 rounded bg-gray-50"
                            title="Read-only"
                          />
                          <span className="text-xs text-gray-500 px-2 py-1">lbs</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <p className="text-gray-500">No equipped items found</p>
              <p className="text-xs text-gray-400 mt-2">Items will appear here after character parsing</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Backpack */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
          <span>🎒</span> Backpack
        </h3>
        
        {!inventory.backpack || inventory.backpack.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">No items in backpack</p>
          </div>
        ) : (
          <div className="space-y-2">
            {inventory.backpack.map((item, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-3">
                <div className="grid md:grid-cols-7 gap-2">
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Name</label>
                    <input
                      type="text"
                      value={item.definition?.name || item.name || ''}
                      readOnly
                      className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50"
                      title="Item data is read-only"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Qty</label>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => updateBackpackItem(index, 'quantity', parseInt(e.target.value) || 1)}
                      className="w-full px-2 py-1 border border-gray-300 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Weight (lbs)</label>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      value={item.definition?.weight || item.weight || 0}
                      readOnly
                      className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
                    <input
                      type="text"
                      value={item.definition?.description || item.description || ''}
                      readOnly
                      className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50 text-xs"
                      title="Read-only"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Equip to</label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          moveToEquipped(index, e.target.value)
                          e.target.value = '' // Reset selector
                        }
                      }}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                      defaultValue=""
                    >
                      <option value="">Select slot...</option>
                      {EQUIPMENT_SLOTS.map(slot => (
                        <option key={slot} value={slot}>
                          {slot.replace('_', ' ')}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Weight Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <span className="font-bold text-blue-800">Total Carried Weight:</span>
          <span className="text-2xl font-bold text-blue-600">{totalWeight()} lbs</span>
        </div>
      </div>
    </div>
  )
}
