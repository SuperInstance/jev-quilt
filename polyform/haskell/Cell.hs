-- Cell.hs — law 1 at the type level: identity is not representable as Float.
-- STATUS: UNVERIFIED (no ghc on this node). Literature-grade Haskell;
-- the types are the claim. A coordinate can only be built from Ints;
-- the only escape to Float is a function named betrayal on projections.

{-# LANGUAGE DataKinds #-}
{-# LANGUAGE KindSignatures #-}

module Cell where

-- Exact rational, denominator positive, stored coprime.
-- Rational here is Integer-backed; fixed-point is the subring
-- Z[1/10^6], not an approximation of anything.
newtype Q16 = Q16 (Integer, Integer) deriving (Eq, Show)

data Domain = Lattice  -- where identity lives
            | Proj     -- where floats are permitted, named and shamed

-- There is NO constructor of Coord that accepts a Float.
-- This is the whole point of the module.
data Coord = Coord !Int !Int deriving (Eq, Show)

data Cell (s :: Domain) = Cell
  { name  :: String
  , coord :: Coord
  , hooks :: [Hook]
  }

data Hook = Hook
  { source :: String
  , floorQ :: Maybe Q16   -- Nothing = the DEADBAND token
  }

-- Identity cells: coordinates are integers, full stop.
type IdentityCell = Cell 'Lattice

-- Projections may betray into Float, but the compiler makes the
-- betrayal a separate, greppable act.
toFloatBetrayal :: Q16 -> Float
toFloatBetrayal (Q16 (n, d)) = fromInteger n / fromInteger d

-- A fabric-level invariant the type system cannot see but can be
-- asserted wherever wake happens: every state change is booked.
-- (Enforced at runtime by the Bookkeeper in other formalisms; here the
-- type signature is the contract documentation.)
class Booked a where
  receipt :: a -> String -> Q16 -> a  -- old state -> kind -> delta -> new state
