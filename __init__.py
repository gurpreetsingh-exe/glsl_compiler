bl_info = {
    "name": "GLSL Compiler",
    "category": "Node",
    "blender": (3, 0, 0),
    "version": (0, 0, 1),
}

try:
    from beeprint import pp
except ImportError:
    print("beeprint is not installed")

import bpy
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
    WindowManager)

from .nodegen import NodeGen

from .Lexer import Lexer
from .Parser import Parser

class COM_PT_Panel(Panel):
    bl_idname = "COM_PT_Panel"
    bl_label = "GLSL Compiler"
    bl_region_type = "UI"
    bl_space_type = "NODE_EDITOR"
    bl_category = "GLSL Compiler"

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "tree_type") and \
            context.space_data.tree_type in {'ShaderNodeTree', 'GeometryNodeTree'} and \
            context.space_data.node_tree

    def draw(self, context):
        gc = context.window_manager.glsl_compiler
        layout = self.layout
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row = row.column()
        row.prop(gc, "filepath")
        row = row.column()
        row.operator("glsl_compiler.compile")

        row = layout.row(align=True)
        row.prop(gc, "debug_ast_output")

class COM_OT_compile(Operator):
    bl_idname = "glsl_compiler.compile"
    bl_label = "Compile"

    @classmethod
    def poll(cls, context):
        gc = context.window_manager.glsl_compiler
        return gc.filepath

    def dump_ast(self, ast):
        print("======= AST dump start =======")
        for a in ast:
            if 'pp' in globals():
                pp(a, indent=4, max_depth=10)
            else:
                print(a)
        print("======== AST dump end ========")


    def execute(self, context):
        gc = context.window_manager.glsl_compiler
        content = ""
        with open(gc.filepath, "r") as f:
            content = f.read()
        tokens = list(Lexer(content).lexfile())
        ast = list(Parser(tokens).parse())
        if gc.debug_ast_output:
            self.dump_ast(ast)
        NodeGen(ast, context).start()
        return {'FINISHED'}

class GLSLCompiler(PropertyGroup):
    filepath: bpy.props.StringProperty(name="Source file", subtype="FILE_PATH",
        # temp
        default="/home/gurpreetsingh/Development/glsl_compiler/shader.glsl")

    debug_ast_output: bpy.props.BoolProperty(name="AST output", default=False)

classes = [
    COM_PT_Panel,
    GLSLCompiler,
    COM_OT_compile,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    WindowManager.glsl_compiler = bpy.props.PointerProperty(type=GLSLCompiler)

def unregister():
    del WindowManager.glsl_compiler

    for cls in classes:
        bpy.utils.unregister_class(cls)
