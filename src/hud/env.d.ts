/** globals */
declare const m: Mithril.Static;
declare const atp: Atp.Static;

/** subinitial.automation API */
declare namespace Atp {
  interface Static {
    send(channel: string): any;
    getHudRoot(): HTMLDivElement;
  }
}

/** mithril.js API */
declare namespace Mithril {
  /** Renders a vnode structure into a DOM element. */
  function render(el: Element, vnodes: Mithril.Children): void;

  /** Mounts a component to a DOM element, enabling it to autoredraw on user events. */
  function mount(element: Element, component: Mithril.ComponentTypes<any, any>): void;
  /** Unmounts a component from a DOM element. */
  function mount(element: Element, component: null): void; // tslint:disable-line unified-signatures

  interface CommonAttributes<Attrs, State> {
    /** The oninit hook is called before a vnode is touched by the virtual DOM engine. */
    oninit?(this: State, vnode: Vnode<Attrs, State>): any;
    /** The oncreate hook is called after a DOM element is created and attached to the document. */
    oncreate?(this: State, vnode: VnodeDOM<Attrs, State>): any;
    /** The onbeforeremove hook is called before a DOM element is detached from the document. If a Promise is returned, Mithril only detaches the DOM element after the promise completes. */
    onbeforeremove?(this: State, vnode: VnodeDOM<Attrs, State>): Promise<any> | void;
    /** The onremove hook is called before a DOM element is removed from the document. */
    onremove?(this: State, vnode: VnodeDOM<Attrs, State>): any;
    /** The onbeforeupdate hook is called before a vnode is diffed in a update. */
    onbeforeupdate?(this: State, vnode: Vnode<Attrs, State>, old: VnodeDOM<Attrs, State>): boolean | void;
    /** The onupdate hook is called after a DOM element is updated, while attached to the document. */
    onupdate?(this: State, vnode: VnodeDOM<Attrs, State>): any;
    /** A key to optionally associate with this element. */
    key?: string | number | undefined;
  }

  interface Hyperscript {
    /** Creates a virtual element (Vnode). */
    (selector: string, ...children: Children[]): Vnode<any, any>;
    /** Creates a virtual element (Vnode). */
    (selector: string, attributes: Attributes, ...children: Children[]): Vnode<any, any>;
    /** Creates a virtual element (Vnode). */
    <Attrs, State>(component: ComponentTypes<Attrs, State>, ...args: Children[]): Vnode<Attrs, State>;
    /** Creates a virtual element (Vnode). */
    <Attrs, State>(
        component: ComponentTypes<Attrs, State>,
        attributes: Attrs & CommonAttributes<Attrs, State>,
        ...args: Children[]
    ): Vnode<Attrs, State>;
    /** Creates a fragment virtual element (Vnode). */
    fragment(attrs: CommonAttributes<any, any> & { [key: string]: any }, children: ChildArrayOrPrimitive): Vnode<any, any>;
    /** Turns an HTML string into a virtual element (Vnode). Do not use trust on unsanitized user input. */
    trust(html: string): Vnode<any, any>;
  }


  interface Redraw {
    /** Manually triggers an asynchronous redraw of mounted components. */
    (): void;
    /** Manually triggers a synchronous redraw of mounted components. */
    sync(): void;
  }

  type Params = object & ParamsRec;

  interface ParamsRec {
    // Ideally, it'd be this:
    // `[key: string | number]: Params | !symbol & !object`
    [key: string]: string | number | boolean | null | undefined | Params;
  }

  interface Static extends Hyperscript {
    mount: typeof mount;
    render: typeof render;
    redraw: Redraw;
  }

  // Vnode children types
  type Child = Vnode<any, any> | string | number | boolean | null | undefined;
  interface ChildArray extends Array<Children> {}
  type Children = Child | ChildArray;
  type ChildArrayOrPrimitive = ChildArray | string | number | boolean;

  /** Virtual DOM nodes, or vnodes, are Javascript objects that represent an element (or parts of the DOM). */
  interface Vnode<Attrs = {}, State = {}> {
    /** The nodeName of a DOM element. It may also be the string [ if a vnode is a fragment, # if it's a text vnode, or < if it's a trusted HTML vnode. Additionally, it may be a component. */
    tag: string | ComponentTypes<Attrs, State>;
    /** A hashmap of DOM attributes, events, properties and lifecycle methods. */
    attrs: Attrs;
    /** An object that is persisted between redraws. In component vnodes, state is a shallow clone of the component object. */
    state: State;
    /** The value used to map a DOM element to its respective item in an array of data. */
    key?: string | number | undefined;
    /** In most vnode types, the children property is an array of vnodes. For text and trusted HTML vnodes, The children property is either a string, a number or a boolean. */
    children?: ChildArrayOrPrimitive | undefined;
    /**
     * This is used instead of children if a vnode contains a text node as its only child.
     * This is done for performance reasons.
     * Component vnodes never use the text property even if they have a text node as their only child.
     */
    text?: string | number | boolean | undefined;
  }

  // In some lifecycle methods, Vnode will have a dom property
  // and possibly a domSize property.
  interface VnodeDOM<Attrs = {}, State = {}> extends Vnode<Attrs, State> {
    /** Points to the element that corresponds to the vnode. */
    dom: Element;
    /** This defines the number of DOM elements that the vnode represents (starting from the element referenced by the dom property). */
    domSize?: number | undefined;
  }

  type _NoLifecycle<T> = Omit<T, keyof Component>;

  interface CVnode<A = {}> extends Vnode<A, ClassComponent<A>> {}

  interface CVnodeDOM<A = {}> extends VnodeDOM<A, ClassComponent<A>> {}

  /**
  * Components are a mechanism to encapsulate parts of a view to make code easier to organize and/or reuse.
  * Any Javascript object that has a view method can be used as a Mithril component.
  * Components can be consumed via the m() utility.
  */
  interface Component<Attrs = {}, State = {}> {
    /** The oninit hook is called before a vnode is touched by the virtual DOM engine. */
    oninit?(this: _NoLifecycle<this & State>, vnode: Vnode<Attrs, _NoLifecycle<this & State>>): any;
    /** The oncreate hook is called after a DOM element is created and attached to the document. */
    oncreate?(this: _NoLifecycle<this & State>, vnode: VnodeDOM<Attrs, _NoLifecycle<this & State>>): any;
    /** The onbeforeremove hook is called before a DOM element is detached from the document. If a Promise is returned, Mithril only detaches the DOM element after the promise completes. */
    onbeforeremove?(this: _NoLifecycle<this & State>, vnode: VnodeDOM<Attrs, _NoLifecycle<this & State>>): Promise<any> | void;
    /** The onremove hook is called before a DOM element is removed from the document. */
    onremove?(this: _NoLifecycle<this & State>, vnode: VnodeDOM<Attrs, _NoLifecycle<this & State>>): any;
    /** The onbeforeupdate hook is called before a vnode is diffed in a update. */
    onbeforeupdate?(this: _NoLifecycle<this & State>, vnode: Vnode<Attrs, _NoLifecycle<this & State>>, old: VnodeDOM<Attrs, _NoLifecycle<this & State>>): boolean | void;
    /** The onupdate hook is called after a DOM element is updated, while attached to the document. */
    onupdate?(this: _NoLifecycle<this & State>, vnode: VnodeDOM<Attrs, _NoLifecycle<this & State>>): any;
    /** Creates a view out of virtual elements. */
    view(this: _NoLifecycle<this & State>, vnode: Vnode<Attrs, _NoLifecycle<this & State>>): Children | null | void;
  }

  /**
  * Components are a mechanism to encapsulate parts of a view to make code easier to organize and/or reuse.
  * Any class that implements a view method can be used as a Mithril component.
  * Components can be consumed via the m() utility.
  */
  interface ClassComponent<A = {}> {
    /** The oninit hook is called before a vnode is touched by the virtual DOM engine. */
    oninit?(vnode: Vnode<A, this>): any;
    /** The oncreate hook is called after a DOM element is created and attached to the document. */
    oncreate?(vnode: VnodeDOM<A, this>): any;
    /** The onbeforeremove hook is called before a DOM element is detached from the document. If a Promise is returned, Mithril only detaches the DOM element after the promise completes. */
    onbeforeremove?(vnode: VnodeDOM<A, this>): Promise<any> | void;
    /** The onremove hook is called before a DOM element is removed from the document. */
    onremove?(vnode: VnodeDOM<A, this>): any;
    /** The onbeforeupdate hook is called before a vnode is diffed in a update. */
    onbeforeupdate?(vnode: Vnode<A, this>, old: VnodeDOM<A, this>): boolean | void;
    /** The onupdate hook is called after a DOM element is updated, while attached to the document. */
    onupdate?(vnode: VnodeDOM<A, this>): any;
    /** Creates a view out of virtual elements. */
    view(vnode: Vnode<A, this>): Children | null | void;
  }

  /**
  * Components are a mechanism to encapsulate parts of a view to make code easier to organize and/or reuse.
  * Any function that returns an object with a view method can be used as a Mithril component.
  * Components can be consumed via the m() utility.
  */
  type FactoryComponent<A = {}> = (vnode: Vnode<A>) => Component<A>;

  /**
  * Components are a mechanism to encapsulate parts of a view to make code easier to organize and/or reuse.
  * Any function that returns an object with a view method can be used as a Mithril component.
  * Components can be consumed via the m() utility.
  */
  type ClosureComponent<A = {}> = FactoryComponent<A>;

  /**
  * Components are a mechanism to encapsulate parts of a view to make code easier to organize and/or reuse.
  * Any Javascript object that has a view method is a Mithril component. Components can be consumed via the m() utility.
  */
  type Comp<Attrs = {}, State = {}> = _NoLifecycle<State> & Component<Attrs, _NoLifecycle<State>>;

  /** Components are a mechanism to encapsulate parts of a view to make code easier to organize and/or reuse. Components can be consumed via the m() utility. */
  type ComponentTypes<A = {}, S = {}> =
    | Component<A, S>
    | { new (vnode: CVnode<A>): ClassComponent<A> }
    | FactoryComponent<A>;

  /** This represents the attributes available for configuring virtual elements, beyond the applicable DOM attributes. */
  interface Attributes extends CommonAttributes<any, any> {
    /** The class name(s) for this virtual element, as a space-separated list. */
    className?: string | undefined;
    /** The class name(s) for this virtual element, as a space-separated list. */
    class?: string | undefined;
    /** Any other virtual element properties, including attributes and event handlers. */
    [property: string]: any;
  }
}
