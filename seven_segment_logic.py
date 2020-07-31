import copy
import numpy as np


# ====================== Client As A Function ======================
def main():
    my_7_seg = SevenSegmentLogic()
    my_12_seg = MultiSegmentLogic(12)

    print("As constructed -------------------")
    print(my_7_seg)

    try:
        my_12_seg.set_num_segs(12)  # should work
        my_7_seg.set_num_segs(8)  # should "throw"
    except ValueError as err:
        print("\nExpected ... " + str(err) + "\n")

    try:
        my_7_seg.eval(1)

    except AttributeError as err:
        print("\nNot Expected... " + str(err) + "\n")

    print("\nFrom 0 - 16: \n")
    for input_x in range(16):
        print("inputX = ", input_x)
        my_7_seg.eval(input_x)
        print("\n| ", end='')
        for k in range(7):
            print(str(my_7_seg.get_val_of_seg(k)) + " | ", end='')
        print()


# ====================== End of Client As A Function ======================
# ====================== BooleanFunc Class ======================

class BooleanFunc:
    # Static members and intended constants
    MAX_TABLE_SIZE = 65536  # that's 16 binary inputs
    MIN_TABLE_SIZE = 2  # that's 1 binary input
    MIN_VALUE = 0
    DEFAULT_TABLE_SIZE = 4
    DEFAULT_FUNC = DEFAULT_TABLE_SIZE * [False]

    # Initializer ("constructor") method -------------------
    def __init__(self, table_size=None, defining_list=None,
                 eval_return_if_error=False):
        """
        Args:
            table_size:
            defining_list:
            eval_return_if_error:
        """
        if not table_size and not defining_list:
            # passed neither list nor size
            table_size = self.DEFAULT_TABLE_SIZE
            defining_list = self.DEFAULT_FUNC
        elif table_size and not defining_list:
            # passed size but no list
            self.valid_table_size(table_size)  # raises, no return
            defining_list = table_size * [False]
        elif not table_size:
            # passed list but no size
            self.valid_defining_list(defining_list)  # raises, no return
            table_size = len(defining_list)
        else:
            # passed both list and size
            self.valid_defining_list(defining_list)
            if len(defining_list) != table_size:
                raise ValueError("Table size does not match list length"
                                 " in constructor.")
        # sanitize bools (e.g. (1.32, "hi", -99)->True, (0.0, "",  # 0)->False)
        eval_return_if_error = bool(eval_return_if_error)
        defining_list = [bool(item) for item in defining_list]

        # assign instance members
        self.eval_return_if_error = eval_return_if_error
        self.state = eval_return_if_error
        self.table_size = table_size
        self.truth_table = np.array(defining_list, dtype=bool)

    def set_truth_table_using(self, rarer_value, inputs_that_produce_rarer_val):
        """Allow the client to mutate the truth table (without changing the
        size, whose immutability we preserve from our original design). """
        if not (self.MIN_VALUE <= len(inputs_that_produce_rarer_val) <=
                self.table_size):
            return False
        # initialize with inputs_that_produce_rarer_val
        if rarer_value is True:
            self.initialize_table(False)

        elif rarer_value is False:
            self.initialize_table(True)

        # set the rarer value
        for i in range(len(inputs_that_produce_rarer_val)):
            the_num = inputs_that_produce_rarer_val[i]
            if self.valid_input(the_num):
                self.truth_table[the_num] = rarer_value
        return True

    # Mutator  -------------------------------
    def eval(self, input_val):
        """a mutator for the state attribute based on the an input integer"""
        if not (self.valid_input(input_val)):
            self.state = self.eval_return_if_error
            return
        # else
        self.state = self.truth_table[input_val]
        return self.state

    # Accessor  -------------------------------
    def get_state(self):
        return self.state

    # Stringizer  -------------------------------
    def __str__(self):
        ret_str = "truth_table: " + str(self.truth_table) + "\nsize = " + str(
            self.table_size) + "\nerror return = " + str(
            self.eval_return_if_error) + "\ncurrent state = " + str(
            self.state) + "\n"
        return ret_str

    # Helper
    @classmethod
    def valid_table_size(cls, size):
        if not isinstance(size, int):
            raise TypeError("Table size must be an int.")
        if not (cls.MIN_TABLE_SIZE <= size <= cls.MAX_TABLE_SIZE):
            raise ValueError("Bad table size passed to constructor"
                             " (legal range: {}-{}).".format(cls.MIN_TABLE_SIZE,
                                                             cls.MAX_TABLE_SIZE))
        # else
        return True

    @classmethod
    def valid_defining_list(cls, the_list):
        if not isinstance(the_list, list):
            raise ValueError("Bad type in constructor. defining_list must be"
                             " type list.")
        if not (cls.MIN_TABLE_SIZE <= len(the_list) <= cls.MAX_TABLE_SIZE):
            raise ValueError("Bad list passed to constructor"
                             " (its length is outside legal range: {}-{"
                             "}).".format(cls.MIN_TABLE_SIZE,
                                          cls.MAX_TABLE_SIZE))
        # else
        return True

    def initialize_table(self, initial_val):
        for i in range(self.table_size):
            self.truth_table[i] = initial_val

    def valid_input(self, eval_input):
        if not isinstance(eval_input, int):
            return False
        if not (self.MIN_VALUE <= eval_input < self.table_size):
            return False
        return True


# ====================== End Of BooleanFunc Class ======================

# ======================= MultiSegmentLogic Class =======================

class MultiSegmentLogic:
    # Static members and intended constants
    MAX_SEGS = 7
    MIN_SEGS = 0
    DEFAULT_SEGS = 7
    DEFAULT_NUM_SEGS = 0

    # Initializer ("constructor") method -------------------
    def __init__(self, num_segs=DEFAULT_NUM_SEGS):
        self.segs = []
        if not self.set_num_segs(num_segs):
            self.num_segs = self.DEFAULT_NUM_SEGS
        self.num_segs = num_segs
        self.segs = [BooleanFunc(num_segs) for i in range(num_segs)]

    # Mutator  -------------------------------
    def set_num_segs(self, num_segs):
        if not self.check_empty_segs(num_segs):
            return False
        # else
        del self.segs
        self.segs = [BooleanFunc(num_segs) for i in range(num_segs)]
        self.num_segs = num_segs
        return True

    def set_segment(self, seg_num, func_for_this_seg):
        # deep copy of func_for_this_seg
        if not self.valid_num_segs(seg_num):
            return False
        # else
        self.segs[seg_num] = copy.deepcopy(func_for_this_seg)
        return True

    # Accessor  -------------------------------
    def get_val_of_seg(self, seg_num):
        if not isinstance(seg_num, int):
            return False
        if not (self.MIN_SEGS <= seg_num < self.MAX_SEGS):
            return False
        return self.segs[seg_num].state

    def eval(self, input):
        for i in range(self.num_segs):
            try:
                self.segs[i].eval(input)
                if self.segs[i] is None:
                    raise AttributeError
            except AttributeError:
                print("Attribute Error")

    @classmethod
    def check_empty_segs(cls, num_segs):
        if num_segs < cls.DEFAULT_NUM_SEGS:
            return False
        return True

    # helper
    def valid_num_segs(self, segs_num):
        if not (self.MIN_SEGS <= segs_num < self.num_segs):
            return False
        return True

    def __str__(self):
        ret_str = "segs: "
        ret_str += str(self.segs[0])
        ret_str += str(self.segs[1])
        ret_str += str(self.segs[2])
        ret_str += str(self.segs[3])
        ret_str += str(self.segs[4])
        ret_str += str(self.segs[5])
        ret_str += str(self.segs[6])
        ret_str += "\nnum segs = " + str(self.num_segs)
        return ret_str


# ======================== End Of MultiSegmentLogic Class ========================

# ============================ SevenSegmentLogic Class ===========================

class SevenSegmentLogic(MultiSegmentLogic):
    # Initializer ("constructor") method -------------------
    def __init__(self):
        # call base class
        super(SevenSegmentLogic, self).__init__(7)
        self.load_boolean_func_for_each_segment()

    # override to base class method
    def set_num_segs(self, num_segs):
        if num_segs != 7:
            raise ValueError("Number of segments is not 7!")
        # else
        # chain to base class method
        super(SevenSegmentLogic, self).set_num_segs(num_segs)

    # helper
    def load_boolean_func_for_each_segment(self):
        # instantiate BooleanFunc of segment_A to segment_G
        segment_a = BooleanFunc(16)
        segment_b = BooleanFunc(16)
        segment_c = BooleanFunc(16)
        segment_d = BooleanFunc(16)
        segment_e = BooleanFunc(16)
        segment_f = BooleanFunc(16)
        segment_g = BooleanFunc(16)
        # set up a flag to determine if the segment rules have been set up
        self.funcs_previously_defined = False

        if not self.funcs_previously_defined:
            # rules of segment A-G
            a_func = [1, 4, 11, 13]
            b_func = [5, 6, 11, 12, 14, 15]
            c_func = [2, 12, 14, 15]
            d_func = [1, 4, 7, 9, 10, 15]
            e_func = [1, 3, 4, 5, 7, 9]
            f_func = [1, 2, 3, 7, 13]
            g_func = [0, 1, 7, 12]

            # use False as rare_value to set up the truth table.
            segment_a.set_truth_table_using(False, a_func)
            segment_b.set_truth_table_using(False, b_func)
            segment_c.set_truth_table_using(False, c_func)
            segment_d.set_truth_table_using(False, d_func)
            segment_e.set_truth_table_using(False, e_func)
            segment_f.set_truth_table_using(False, f_func)
            segment_g.set_truth_table_using(False, g_func)
            self.funcs_previously_defined = True

        self.set_segment(0, segment_a)
        self.set_segment(1, segment_b)
        self.set_segment(2, segment_c)
        self.set_segment(3, segment_d)
        self.set_segment(4, segment_e)
        self.set_segment(5, segment_f)
        self.set_segment(6, segment_g)

    def valid_num_segs(self, segs_num):
        if not (self.MIN_SEGS <= segs_num < self.MAX_SEGS):
            return False
        return True


# ============================= End Of SevenSegmentLogic Class ===================

# ================================== Main Program ================================

if __name__ == "__main__":
    main()
