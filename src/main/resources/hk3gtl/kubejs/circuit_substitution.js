// priority: -10000
// 加工用透镜 / 模具 → 一个不消耗的编程电路。最后处理模组原配方和其他 KJS 新增配方。
// 保留现有 lens_module / mold_module 的电路编号与加速配方；按实际材料、数量、产物去重。
// 制作透镜、模具、场形状本身的配方不替换工具；压模器的导线加工归回线材轧机。
ServerEvents.recipes(event => {
    let JsonRecipe = Java.loadClass('dev.latvian.mods.kubejs.recipe.JsonRecipeJS')
    let GTRecipeJS = Java.loadClass('com.gregtechceu.gtceu.integration.kjs.recipe.GTRecipeSchema$GTRecipeJS')
    let GTRecipeType = Java.loadClass('com.gregtechceu.gtceu.api.recipe.GTRecipeType')
    let Serializer = Java.loadClass('com.gregtechceu.gtceu.api.recipe.GTRecipeSerializer')
    let Parser = Java.loadClass('com.google.gson.JsonParser')
    let ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
    let FluidIngredient = Java.loadClass('com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient')
    let FluidTagValue = Java.loadClass('com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient$TagValue')
    let TagContext = Java.loadClass('dev.latvian.mods.kubejs.item.ingredient.TagContext')
    let Registries = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
    let gtTypes = Object.create(null)
    Registries.RECIPE_TYPE.forEach(type => {
        if (type instanceof GTRecipeType) gtTypes[String(Registries.RECIPE_TYPE.getKey(type))] = true
    })

    let casting = ['ingot', 'plate', 'gear', 'small_gear', 'credit', 'bottle', 'nugget', 'ball', 'cylinder', 'block', 'anvil', 'name', 'rotor', 'pill']
    let extruding = ['plate', 'rod', 'ingot', 'block', 'gear', 'small_gear', 'ring', 'bolt', 'wire', 'cell', 'tiny_pipe', 'small_pipe', 'normal_pipe', 'large_pipe', 'huge_pipe', 'bottle', 'foil', 'long_rod', 'rotor']
    let colors = { white: 32, black: 31, red: 30, green: 29, brown: 28, blue: 27, purple: 26, cyan: 25, light_gray: 24, gray: 23, pink: 22, lime: 21, yellow: 20, light_blue: 19, magenta: 18, orange: 17 }
    let toolItems = Object.create(null)
    casting.forEach((name, i) => { toolItems['gtceu:' + name + '_casting_mold'] = i + 1 })
    extruding.forEach((name, i) => { toolItems['gtceu:' + name + '_extruder_mold'] = i + 1 })
    toolItems['kubejs:ingot_field_shape'] = 1
    toolItems['kubejs:ball_field_shape'] = 2
    toolItems['kubejs:non_linear_optical_lens'] = 15
    toolItems['gtladditions:spacetime_lens'] = 16
    Object.keys(colors).forEach(color => {
        let config = colors[color]
        toolItems[color === 'white' ? 'gtceu:glass_lens' : 'gtceu:' + color + '_glass_lens'] = config
        Ingredient.of('#forge:lenses/' + color).getItemIds().forEach(id => { toolItems[String(id)] = config })
    })
    let idsCache = Object.create(null)
    let fluidCache = Object.create(null)
    let stats = { scanned: 0, converted: 0, duplicates: 0, wireRemoved: 0, wireMoved: 0, derived: 0, circuitsReassigned: 0 }

    let clone = value => JSON.parse(JSON.stringify(value))
    let gson = value => Parser.parseString(JSON.stringify(value)).getAsJsonObject()
    function stable(value) {
        if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']'
        if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + stable(value[k])).join(',') + '}'
        return JSON.stringify(value)
    }
    function atoms(value) {
        if (Array.isArray(value)) return value.reduce((out, v) => out.concat(atoms(v)), [])
        if (!value || typeof value !== 'object') return []
        if (value.ingredient !== undefined) return atoms(value.ingredient)
        if (value.item) return [{ item: String(value.item) }]
        if (value.tag) return [{ tag: String(value.tag) }]
        if (value.items) return atoms(value.items)
        if (value.children) return atoms(value.children)
        return []
    }
    function isToolItem(id) {
        return toolItems[id] !== undefined || /_(casting_mold|extruder_mold|field_shape|lens)$/.test(id)
    }
    function toolConfig(value) {
        let choices = atoms(value)
        if (!choices.length) return null
        let configs = choices.map(choice => {
            if (choice.tag && choice.tag.indexOf('forge:lenses/') === 0) return colors[choice.tag.slice('forge:lenses/'.length)] || 16
            if (choice.tag && choice.tag === 'forge:lenses') return 32
            if (choice.tag && /^kubejs:laser_\d+$/.test(choice.tag)) return 33 - Number(choice.tag.slice('kubejs:laser_'.length))
            if (choice.item && isToolItem(choice.item)) return toolItems[choice.item] === undefined ? 16 : toolItems[choice.item]
            return null
        })
        return configs.every(n => n !== null) ? Math.min.apply(null, configs) : null
    }
    function circuitConfig(value) {
        if (!value || Array.isArray(value)) return null
        if (value.ingredient !== undefined) return circuitConfig(value.ingredient)
        if (value.type === 'gtceu:circuit') return Number(value.configuration)
        if (value.item !== 'gtceu:programmed_circuit') return null
        if (value.nbt && typeof value.nbt === 'object' && value.nbt.Configuration !== undefined) return Number(value.nbt.Configuration)
        let found = String(value.nbt || '').match(/Configuration\s*:\s*(-?\d+)/)
        return found ? Number(found[1]) : null
    }
    function catalyst(entry) { return entry.chance === 0 }
    function itemIds(ingredient) {
        let key = stable(ingredient)
        if (idsCache[key] !== undefined) return idsCache[key]
        let out = []
        Ingredient.of(ingredient).getItemIds().forEach(id => out.push(String(id)))
        out.sort()
        idsCache[key] = out
        return out
    }
    function itemKey(content) {
        if (!content || typeof content !== 'object') return content
        let inner = content.ingredient === undefined ? content : content.ingredient
        let count = content.count === undefined ? 1 : content.count
        // 普通物品 / 标签按当前注册表中的可用物品统一；NBT 原样参与身份比较。
        let hasNbt = /"(?:nbt|configuration|data)"/.test(stable(inner))
        let ids = hasNbt ? [] : itemIds(inner)
        return { count: count, ingredient: ids.length ? ids : inner }
    }
    function fluidKey(content) {
        if (!content || typeof content !== 'object' || !content.value) return content
        let selector = stable(content.value)
        if (fluidCache[selector] === undefined) {
            let fluidIngredient = FluidIngredient.fromJson(gson({ amount: 1, value: content.value }))
            let fluidIds = []
            // 首次 recipes 回调时原生流体标签尚未绑定，使用本轮 KJS TagContext。
            fluidIngredient.values.forEach(value => {
                if (value instanceof FluidTagValue) TagContext.INSTANCE.getValue().getTag(value.getTag()).forEach(holder => fluidIds.push(String(Registries.FLUID.getKey(holder.value()))))
                else fluidIds.push(String(value.serialize().get('fluid').getAsString()))
            })
            fluidIds.sort()
            fluidCache[selector] = fluidIds.filter((id, i, all) => i === 0 || id !== all[i - 1])
        }
        let normalized = { amount: content.amount, value: fluidCache[selector].length ? fluidCache[selector] : content.value }
        if (content.nbt !== undefined) normalized.nbt = content.nbt
        return normalized
    }
    function contentKey(entry, capability) {
        let normalized = clone(entry)
        normalized.chance = entry.chance === undefined ? 10000 : entry.chance
        normalized.maxChance = entry.maxChance === undefined ? 10000 : entry.maxChance
        normalized.tierChanceBoost = entry.tierChanceBoost === undefined ? 0 : entry.tierChanceBoost
        normalized.content = capability === 'item' ? itemKey(entry.content) : capability === 'fluid' ? fluidKey(entry.content) : entry.content
        return normalized
    }
    function mapKey(map, consumedOnly, omitEu) {
        let result = Object.create(null)
        Object.keys(map || {}).sort().forEach(capability => {
            if (omitEu && capability === 'eu') return
            let entries = (map[capability] || []).filter(c => !consumedOnly || !catalyst(c))
            if (entries.length) result[capability] = entries.map(c => stable(contentKey(c, capability))).sort()
        })
        return result
    }
    function bodyKey(json) {
        return stable([json.type, mapKey(json.inputs, true, false), mapKey(json.outputs, false, false), mapKey(json.tickOutputs, false, false)])
    }
    function otherCatalysts(json) {
        let result = Object.create(null)
        Object.keys(json.inputs || {}).sort().forEach(capability => {
            let entries = json.inputs[capability].filter(c => catalyst(c) && (capability !== 'item' || (toolConfig(c.content) === null && circuitConfig(c.content) === null)))
            if (entries.length) result[capability] = entries.map(c => stable(contentKey(c, capability))).sort()
        })
        return result
    }
    function semanticKey(json, key) {
        let data = clone(json.data || {})
        delete data.euTier
        return stable([key, otherCatalysts(json), mapKey(json.tickInputs, false, true), json.recipeConditions || [], data, json.inputChanceLogics || {}, json.outputChanceLogics || {}, json.tickInputChanceLogics || {}, json.tickOutputChanceLogics || {}])
    }
    function makesTool(json) {
        return (((json.outputs || {}).item || []).some(c => atoms(c.content).some(a => a.item && isToolItem(a.item))))
    }
    function hasTools(json) {
        return ((json.inputs || {}).item || []).some(c => catalyst(c) && toolConfig(c.content) !== null) && !makesTool(json)
    }
    function legacy(id) { return /^(lens_module|mold_module):/.test(id) }
    function eut(json) { return (((json.tickInputs || {}).eu || []).reduce((n, c) => n + Number(c.content || 0), 0)) }
    function preferred(a, b) {
        if (legacy(a.id) !== legacy(b.id)) return legacy(a.id) ? -1 : 1
        if (legacy(a.id) && !!a.derived !== !!b.derived) return a.derived ? 1 : -1
        if (Number(a.json.duration) !== Number(b.json.duration)) return Number(a.json.duration) - Number(b.json.duration)
        if (eut(a.json) !== eut(b.json)) return eut(a.json) - eut(b.json)
        return a.id < b.id ? -1 : a.id > b.id ? 1 : 0
    }

    function mayUseTool(value) {
        if (value == null) return false
        if (value.isJsonArray()) {
            let entries = value.getAsJsonArray()
            for (let i = 0; i < entries.size(); i++) if (mayUseTool(entries.get(i))) return true
            return false
        }
        if (!value.isJsonObject()) return false
        let object = value.getAsJsonObject()
        if (object.has('ingredient')) return mayUseTool(object.get('ingredient'))
        if (object.has('item') && object.get('item').isJsonPrimitive()) return isToolItem(String(object.get('item').getAsString()))
        if (object.has('tag') && object.get('tag').isJsonPrimitive()) {
            let tag = String(object.get('tag').getAsString())
            return /^forge:lenses(?:\/|$)|^kubejs:laser_\d+$/.test(tag)
        }
        return mayUseTool(object.get('items')) || mayUseTool(object.get('children'))
    }
    function mayHaveTools(json) {
        let inputs = json.getAsJsonObject('inputs')
        let items = inputs == null ? null : inputs.getAsJsonArray('item')
        if (items == null) return false
        for (let i = 0; i < items.size(); i++) {
            let entry = items.get(i).getAsJsonObject()
            let chance = entry.get('chance')
            if (chance != null && chance.isJsonPrimitive() && chance.getAsJsonPrimitive().isNumber() &&
                chance.getAsDouble() === 0 && mayUseTool(entry.get('content'))) return true
        }
        return false
    }
    function body(record) {
        if (!record.json) {
            record.json = JSON.parse(String(record.ref.json))
            record.json.type = record.type
        }
        return record.json
    }
    let originals = []
    let added = []
    function snapshot(ref, isAdded) {
        if (ref.removed) return
        let type = String(ref.getType())
        if (!gtTypes[type]) return
        if (isAdded || ref.hasChanged()) ref.serialize()
        let record = { id: String(ref.getId()), type: type, ref: ref, added: isAdded }
        record.affected = legacy(record.id) || (mayHaveTools(ref.json) && hasTools(body(record)))
        stats.scanned++
        ;(isAdded ? added : originals).push(record)
    }
    event.originalRecipes.values().forEach(ref => snapshot(ref, false))
    event.addedRecipes.forEach(ref => snapshot(ref, true))

    let retired = []
    let expanded = []
    let expandTypes = Object.create(null)
    added.filter(r => r.affected).forEach(r => { expandTypes[r.type] = true })
    // 无模具的同类冷凝配方也派生反熵配方，必须一起展开以预留其电路编号。
    expandTypes['gtceu:vacuum_freezer'] = true
    // GTCEu 在 recipes 回调之后把新增 GTRecipeJS 再构建一次，并派生光子/聚焦/冷凝配方。
    // 先用原类型公开的 Builder 展开这些配方，再统一替换和去重，最后使用 JsonRecipeJS 注册。
    // JsonRecipeJS 不再进入 GTCEu 的二次 Builder 通道；不能只标记 removed，否则插件仍可能重建它。
    function expand(record) {
        if ((!record.affected && !expandTypes[record.type]) || !(record.ref instanceof GTRecipeJS)) { expanded.push(record); return }
        // KJS 条件包装为 {type, data}，原生 GT Codec 要求条件字段直接放在 type 同层。
        let nativeJson = clone(body(record))
        if (nativeJson.recipeConditions) nativeJson.recipeConditions = nativeJson.recipeConditions.map(condition => {
            let json = clone(condition.data || condition)
            json.type = condition.type
            return json
        })
        let recipe = Serializer.SERIALIZER.fromJson(new ResourceLocation(record.id), gson(nativeJson))
        let builder = recipe.recipeType['recipeBuilder(net.minecraft.resources.ResourceLocation,java.lang.Object[])'](record.ref.idWithoutType(), [])
        builder.duration = recipe.duration
        builder.data = recipe.data.copy()
        builder.isFuel = recipe.isFuel()
        // input / output 同时也是重载方法，Rhino 读取时需明确取公开字段。
        builder.getClass().getField('input').get(builder).putAll(recipe.inputs)
        builder.getClass().getField('output').get(builder).putAll(recipe.outputs)
        builder.tickInput.putAll(recipe.tickInputs)
        builder.tickOutput.putAll(recipe.tickOutputs)
        builder.inputChanceLogic.putAll(recipe.inputChanceLogics)
        builder.outputChanceLogic.putAll(recipe.outputChanceLogics)
        builder.tickInputChanceLogic.putAll(recipe.tickInputChanceLogics)
        builder.tickOutputChanceLogic.putAll(recipe.tickOutputChanceLogics)
        builder.conditions.addAll(recipe.conditions)
        builder.researchRecipeEntries().addAll(record.ref.researchRecipeEntries())
        builder.save(finished => {
            let json = JSON.parse(String(finished.serializeRecipe()))
            let id = String(finished.getId())
            expanded.push({ id: id, type: json.type, json: json, ref: null, added: true, affected: hasTools(json) || legacy(id), derived: id !== record.id })
            if (id !== record.id) stats.derived++
        })
        retired.push(record.ref)
    }
    added.forEach(expand)

    // 后声明的 KJS 配方覆盖同 ID 的原配方，保持 KubeJS 的正常优先级。
    let byId = Object.create(null)
    let shadowed = []
    originals.concat(expanded).forEach(record => {
        if (byId[record.id] && byId[record.id].ref) shadowed.push(byId[record.id].ref)
        byId[record.id] = record
    })
    let records = Object.keys(byId).map(id => byId[id])

    // 导线挤压配方与线材轧机重叠：已有轧线途径则移除；唯一途径移入轧线，材料/产量/功率保持。
    let wireTypes = Object.create(null)
    records.filter(r => r.type === 'gtceu:wiremill').forEach(r => { wireTypes[stable([mapKey(body(r).inputs, true, false), mapKey(r.json.outputs, false, false)])] = true })
    records = records.filter(record => {
        if (record.type !== 'gtceu:extruder') return true
        body(record)
        let wireOutputs = ((record.json.outputs || {}).item || []).filter(c => atoms(c.content).some(a => a.item && /(?:_wire|_cable)$/.test(a.item)))
        if (!wireOutputs.length) return true
        let key = stable([mapKey(record.json.inputs, true, false), mapKey(record.json.outputs, false, false)])
        if (wireTypes[key]) {
            if (record.ref) retired.push(record.ref)
            stats.wireRemoved++
            return false
        }
        if (record.ref) retired.push(record.ref)
        record.ref = null
        record.added = true
        record.affected = true
        record.json = clone(record.json)
        record.type = record.json.type = 'gtceu:wiremill'
        record.id = 'circuit_tools:wiremill/' + record.id.replace(':', '/').replace(/\//g, '_')
        record.preferredCircuit = wireOutputs.some(c => atoms(c.content).some(a => a.item && /(?:^|:)fine_|_fine_wire$/.test(a.item))) ? 3 : 1
        stats.wireMoved++
        return true
    })

    let affectedTypes = new Set(records.filter(r => r.affected || (r.added && r.ref === null)).map(r => r.type))
    let groups = Object.create(null)
    let kept = []
    records.forEach(record => {
        if (!affectedTypes.has(record.type)) {
            kept.push(record)
            return
        }
        let key = bodyKey(body(record))
        if (!groups[key]) groups[key] = []
        groups[key].push(record)
    })
    Object.keys(groups).sort().forEach(key => {
        let group = groups[key]
        if (!group.some(r => r.affected)) { kept.push.apply(kept, group); return }
        let chosen = []
        let overrides = group.filter(r => legacy(r.id))
        if (overrides.length) chosen.push(overrides.sort(preferred)[0])
        else {
            let semantic = Object.create(null)
            group.forEach(r => {
                let sk = semanticKey(r.json, key)
                if (!semantic[sk]) semantic[sk] = []
                semantic[sk].push(r)
            })
            Object.keys(semantic).forEach(sk => { chosen.push(semantic[sk].sort(preferred)[0]) })
        }
        group.forEach(r => {
            if (chosen.indexOf(r) < 0) { if (r.ref) retired.push(r.ref); stats.duplicates++ }
        })
        chosen.forEach(r => { r.affected = true; kept.push(r) })
    })

    // GT 查找树不使用材料数量；缺少流体的配方还可能遮住同电路、额外带流体的配方。
    // 按实际材料种类检查相等/包含关系，保留显式 KJS 编号，给冲突的其它工艺分配空编号。
    function searchInputs(json) {
        let keys = Object.create(null)
        Object.keys(json.inputs || {}).forEach(capability => {
            if (capability !== 'item' && capability !== 'fluid') return
            json.inputs[capability].forEach(entry => {
                if (capability === 'item' && catalyst(entry) && (toolConfig(entry.content) !== null || circuitConfig(entry.content) !== null)) return
                let material = capability === 'item' ? itemKey(entry.content).ingredient : fluidKey(entry.content).value
                keys[capability + ':' + stable(material)] = true
            })
        })
        return Object.keys(keys).sort()
    }
    function isSubset(a, b) { return a.every(key => b.indexOf(key) >= 0) }
    let occupied = Object.create(null)
    function reserve(record, config, keys) {
        if (!occupied[record.json.type]) occupied[record.json.type] = Object.create(null)
        let bucket = occupied[record.json.type]
        if (!bucket[config]) bucket[config] = []
        bucket[config].push({ id: record.id, keys: keys })
    }
    function collides(record, config, keys) {
        let bucket = occupied[record.json.type] || {}
        return (bucket[config] || []).some(other => other.id !== record.id && (isSubset(keys, other.keys) || isSubset(other.keys, keys)))
    }
    let controlRows = kept.filter(r => r.affected).sort(preferred)
    let controlTypes = new Set(controlRows.map(r => r.type))
    kept.filter(r => !r.affected && controlTypes.has(r.type)).forEach(record => {
        let inputs = (record.json.inputs || {}).item || []
        let configs = inputs.filter(catalyst).map(c => circuitConfig(c.content)).filter(config => config !== null)
        if (!configs.length) return
        let keys = searchInputs(record.json)
        configs.forEach(config => reserve(record, config, keys))
    })
    controlRows.forEach(record => {
        let json = record.json
        let entries = ((json.inputs || {}).item || [])
        let tools = entries.filter(c => catalyst(c) && toolConfig(c.content) !== null)
        let circuits = entries.filter(c => catalyst(c) && circuitConfig(c.content) !== null)
        if (!tools.length && !circuits.length) return
        let config = record.preferredCircuit !== undefined ? record.preferredCircuit : circuits.length ? circuitConfig(circuits[0].content) : toolConfig(tools[0].content)
        let keys = searchInputs(json)
        if (collides(record, config, keys)) {
            let candidate = 1
            while (candidate <= 32 && collides(record, candidate, keys)) candidate++
            if (candidate > 32) throw new Error('同一输入需要超过 32 个电路配置：' + record.id)
            config = candidate
            stats.circuitsReassigned++
        }
        reserve(record, config, keys)
        record.json = clone(json)
        record.json.inputs.item = entries.filter(c => !(catalyst(c) && (toolConfig(c.content) !== null || circuitConfig(c.content) !== null)))
        record.json.inputs.item.push({ content: { type: 'gtceu:sized', count: 1, ingredient: { type: 'gtceu:circuit', configuration: config } }, chance: 0, maxChance: 10000, tierChanceBoost: 0 })
        if (record.ref) retired.push(record.ref)
        record.ref = null
        record.added = true
        stats.converted++
    })

    retired.concat(shadowed).forEach(ref => { ref.remove(); ref.newRecipe = false })
    kept.filter(record => record.added && record.ref === null).forEach(record => {
        let recipe = new JsonRecipe()
        recipe.type = event.getRecipeFunction(record.json.type)
        recipe.json = gson(record.json)
        recipe.originalJson = recipe.json
        recipe.newRecipe = true
        recipe.changed = true
        recipe.initValues(false)
        recipe.id = new ResourceLocation(record.id)
        event.addRecipe(recipe, true)
    })
    console.info('[电路替换] 扫描 ' + stats.scanned + '，统一 ' + stats.converted + '，重复移除 ' + stats.duplicates + '，导线移除/归位 ' + stats.wireRemoved + '/' + stats.wireMoved + '，派生展开 ' + stats.derived + '，冲突电路调整 ' + stats.circuitsReassigned)
})
